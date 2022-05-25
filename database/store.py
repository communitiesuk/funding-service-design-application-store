import datetime
import uuid
from operator import itemgetter
from typing import List

from config import NOTIFY_TEMPLATE_SUBMIT_APPLICATION
from database.initial_data import fund_round_sections
from database.initial_data import initial_application_store_state
from dateutil import parser as date_parser
from dateutil.tz import UTC
from external_services.data import get_fund
from external_services.data import get_round
from external_services.models.account import AccountMethods
from external_services.models.notification import Notification


class ApplicationDataAccessObject(object):
    """
    A data interface to our currently in-memory data store
    """

    def __init__(self):
        self._applications: dict = {}

    @property
    def applications_index(self) -> dict:
        """
        A dictionary of summary information for applications
        for search purposes

        Returns:
            dict of metadata for each application
        """
        applications = {}
        for application_id, application in self._applications.items():
            application_summary = {
                "id": application.get("id"),
                "account_id": application.get("account_id"),
                "status": application.get("status"),
                "fund_id": application.get("fund_id"),
                "round_id": application.get("round_id"),
                "project_name": application.get("project_name", ""),
                "last_edited": application.get("last_edited"),
                "started_at": application.get("started_at"),
                "date_submitted": application.get("date_submitted"),
            }
            applications.update({application.get("id"): application_summary})
        return applications

    def create_application(self, account_id, fund_id, round_id):
        """
        Mints a fresh application for a given account_id, fund and round

        Args:
            account_id: (str) The account_id of the user
            fund_id: (str) The id of the fund to create an application for
            round_id: (str) The id of the round to create an application for
        """
        sections = self._get_blank_sections(fund_id, round_id)
        application_id, new_application = self._set_attributes(
            account_id, fund_id, round_id, sections
        )
        self._applications.update({application_id: new_application})
        return new_application

    def _get_blank_sections(self, fund_id: str, round_id: str):
        """
        Get the list of sections required to populate a blank
        application for a fund round

        Args:
            fund_id: (str) The id of the fund
            round_id: (str) The id of the fund round

        Returns:
            A list of json sections to populate the form
        """
        fund = get_fund(fund_id)
        fund_round = get_round(fund_id, round_id)
        if fund and fund_round:
            sections = fund_round_sections.get(":".join([fund_id, round_id]))
            if not sections:
                raise Exception(
                    f"Could not find form sections for {fund_id} - {round_id}"
                )
            return sections.copy()
        raise Exception(
            f"Could not find fund round for {fund_id} - {round_id}"
        )

    def submit_application(self, application_id):
        """
        Sets an application status to SUBMITTED, adds a date_submitted
        timestamp and sends a notification with the full application
        content to the account holder's email address
        Args:
            application_id: (str) the id of the application to submit
        Returns:
            The application json
        """
        application = self._applications[application_id]
        application["date_submitted"] = datetime.datetime.now(
            datetime.timezone.utc
        ).strftime("%Y-%m-%d %H:%M:%S")
        self._update_statuses(application_id)
        # Get Account Email
        account = AccountMethods.get_account(
            account_id=application.get("account_id")
        )

        # Send notification
        Notification.send(
            NOTIFY_TEMPLATE_SUBMIT_APPLICATION,
            account.email,
            {"application": self._applications[application_id]},
        )
        return self._applications[application_id]

    def get_section(self, application_id, section_name):
        """
        Returns a single section of an application

        Args:
            application_id: (str) The id of the application
            section_name: (str) The name of the section
        """
        return self._applications[application_id]["sections"][section_name]

    def _find_answer_by_key(self, data: dict, target):
        """
        Finds an answer value from a target key name if it
        exists somewhere in the application

        Args:
            data: (dict) the application dict
            target: (str) the key name of the application question field
                eg. "your-project-name"
        """
        for key, value in data.items():
            if isinstance(value, dict):
                return self._find_answer_by_key(value, target)
            elif isinstance(value, List):
                for item in value:
                    return self._find_answer_by_key(item, target)
            elif key == "key" and value == target:
                answer = data.get("answer")
                if answer:
                    return answer

    def put_section(self, application_id, section_name, new_json):
        """
        Updates a section of the application at section_name

        Args:
            application_id: The id of the application to update
            section_name: The name of the section to update
            new_json: The payload of data to update.
                This currently expects a json object in the form:
                {
                    "questions": section_questions,
                    "section_name": section_name,
                    "metadata": section_metadata
                }
        """
        # Find matching section
        try:
            sections = self._applications[application_id]["sections"]
        except KeyError:
            return None

        section_index = None
        for index, section in enumerate(sections):
            if section["section_name"].lower() == section_name.lower():
                section_index = index
                break
        # If section found, update with put data
        if section_index is not None:
            sections[section_index] = new_json
            # Update application statuses
            self._update_statuses(application_id)
            # Set last edited
            self._applications[application_id][
                "last_edited"
            ] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # IF section includes "your-project-name" field
            # THEN update application project name
            project_name = self._find_answer_by_key(
                new_json, "your-project-name"
            )
            if project_name:
                self._applications[application_id][
                    "project_name"
                ] = project_name
            return self._applications[application_id]["sections"][
                section_index
            ]
        return None

    def get_application(self, application_id: str):
        """
        Get an individual application

        Args:
            application_id: (str) The id of the application

        Returns:
            Dict of application data
        """
        return self._applications.get(application_id)

    def get_applications(self):
        """
        Get a list of all applications

        Returns:
            List of applications
        """
        return [
            application
            for application_id, application in self._applications.items()
        ]

    @staticmethod
    def _set_attributes(
        account_id: str, fund_id: str, round_id: str, sections: List
    ) -> tuple:
        """
        Sets the default attributes of a new application

        Args:
            account_id: (str) The account_id to set the application for
            fund_id: (str) The id of the fund the application is for
            round_id: (str) The id of the round the application is for
            sections: (List) The list of form sections for the application
        """
        application = {}
        date_started = datetime.datetime.now(datetime.timezone.utc)
        application["id"] = str(uuid.uuid4())  # cant be uuid in restx handler
        application["status"] = "NOT_STARTED"
        application["account_id"] = account_id
        application["fund_id"] = fund_id
        application["round_id"] = round_id
        application["started_at"] = date_started.strftime("%Y-%m-%d %H:%M:%S")
        for section in sections:
            for question in section.get("questions"):
                question.update({"status": "NOT_STARTED"})
        application["sections"] = sections
        return application["id"], application

    def _update_statuses(self, application_id: str):
        """
        Updates the statuses for an entire application,
        sections and questions

        Args:
            application_id: The application id
        """
        self._update_question_statuses(application_id)
        self._update_section_statuses(application_id)
        self._update_status(application_id)

    def _update_question_statuses(self, application_id: str):
        """
        Updates the question statuses of each question if a value is present

        Args:
            application_id: The application id
        """
        application = self._applications[application_id]
        for section in application["sections"]:
            for question in section["questions"]:
                for field in question["fields"]:
                    if application.get("date_submitted"):
                        question["status"] = "SUBMITTED"
                    elif field["answer"]:
                        question["status"] = "IN_PROGRESS"
                question["status"] = question.get("status", "NOT_STARTED")
        self._applications.update({application_id: application})

    def _update_section_statuses(self, application_id: str):
        """
        Updates the question statuses of each question if a value is present

        Args:
            application_id: The application id
        """
        application = self._applications[application_id]
        for section in application["sections"]:
            for question in section["questions"]:
                if application.get("date_submitted"):
                    section["status"] = "SUBMITTED"
                    break
                elif question["status"] == "IN_PROGRESS":
                    section["status"] = "IN_PROGRESS"
                    break
            section["status"] = section.get("status", "NOT_STARTED")
        self._applications.update({application_id: application})

    def _update_status(self, application_id: str):
        """
        Updates the application status for an entire application,
        based on status of individual sections

        Args:
            application_id: The application id
        """
        application = self._applications[application_id]
        section_statuses = [
            section["status"] for section in application["sections"]
        ]
        if "IN_PROGRESS" in section_statuses:
            status = "IN_PROGRESS"
        elif "COMPLETED" in section_statuses:
            status = "COMPLETED"
        elif "SUBMITTED" in section_statuses:
            status = "SUBMITTED"
        else:
            status = "NOT_STARTED"
        application["status"] = status
        self._applications.update({application_id: application})

    def get_status(self, application_id: str):
        """
        Summary:
            Get status of application and questions
        Args:
            application_id: Takes an application_id
        Returns:
            Summary of application and assessment status of each question
        """
        application_summary = self.applications_index.get(application_id)
        if application_summary:
            sections = []
            for section in self._applications[application_id].get("sections"):
                questions = []
                status = "NOT_STARTED"
                for question in section.get("questions"):
                    questions.append(
                        {
                            "question": question.get("question"),
                            "status": question.get("status"),
                        }
                    )
                status_values = [question["status"] for question in questions]
                if "IN_PROGRESS" in status_values:
                    status = "IN_PROGRESS"
                elif "COMPLETED" in status_values:
                    status = "COMPLETED"
                sections.append({"status": status, "questions": questions})

            application_summary.update({"sections": sections})
            return application_summary

    def search_applications(self, params):
        """
        Returns a list of applications matching required params
        """
        matching_applications = []
        datetime_start = params.get("datetime_start")
        datetime_end = params.get("datetime_end")
        fund_id = params.get("fund_id")
        account_id = params.get("account_id")
        status_only = params.get("status_only")
        id_contains = params.get("id_contains")
        order_by = params.get("order_by", "id")
        order_rev = params.get("order_rev") == "1"

        for application_id, application in self.applications_index.items():
            match = True

            # Exclude results if given parameters are not a match
            if status_only and status_only.replace(
                " ", "_"
            ).upper() != application.get("status"):
                match = False

            if id_contains and id_contains not in application.get("id"):
                match = False

            if fund_id and fund_id != application.get("fund_id"):
                match = False

            if account_id and account_id != application.get("account_id"):
                match = False

            if datetime_start:
                start = date_parser.parse(datetime_start).astimezone(UTC)
                if start > application["date_submitted"].astimezone(UTC):
                    match = False

            if datetime_end:
                end = date_parser.parse(datetime_end).astimezone(UTC)
                if application["date_submitted"].astimezone(UTC) > end:
                    match = False

            if match:
                matching_applications.append(application)

        if order_by and order_by in [
            "id",
            "status",
            "account_id",
            "assessment_deadline",
        ]:
            matching_applications = sorted(
                matching_applications,
                key=itemgetter(order_by),
                reverse=order_rev,
            )

        return matching_applications


# An in memory data object instance

APPLICATIONS = ApplicationDataAccessObject()
APPLICATIONS._applications = initial_application_store_state
