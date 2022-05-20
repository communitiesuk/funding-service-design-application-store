import datetime
import uuid
from operator import itemgetter
from typing import List

from database.initial_data import fund_round_sections
from database.initial_data import initial_application_store_state
from dateutil import parser as date_parser
from dateutil.tz import UTC
from external_data.data import get_fund
from external_data.data import get_round


class ApplicationDataAccessObject(object):
    """
    A data interface to our currently in-memory data store
    """

    def __init__(self):
        self._applications: dict = {}

    @property
    def applications_index(self) -> dict:
        applications = {}
        for application_id, application in self._applications.items():
            application_summary = {
                "id": application.get("id"),
                "status": application.get("status"),
                "account_id": application.get("account_id"),
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
        sections = self._get_sections(fund_id, round_id)
        application_id, new_application = self._set_attributes(
            account_id, fund_id, round_id, sections
        )
        self._applications.update({application_id: new_application})
        return new_application

    def _get_sections(self, fund_id: str, round_id: str):
        fund = get_fund(fund_id)
        fund_round = get_round(fund_id, round_id)
        if fund and fund_round:
            sections = fund_round_sections.get(":".join([fund_id, round_id]))
            if not sections:
                raise Exception(
                    f"Could not find form sections for {fund_id} - {round_id}"
                )
            return sections
        raise Exception(
            f"Could not find fund round for {fund_id} - {round_id}"
        )

    def submit_application(self, application_id):
        self._applications[application_id][
            "date_submitted"
        ] = datetime.datetime.now(datetime.timezone.utc).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        self._update_statuses(application_id)
        return self._applications[application_id]

    def get_section(self, application_id, section_name):
        return self._applications[application_id]["sections"][section_name]

    def _find_value_by_key(self, data: dict, target):
        for key, value in data.items():
            if isinstance(value, dict):
                yield from self._find_value_by_key(value, target)
            elif key == target:
                yield value

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
        # Find matching section, update with put data
        section_index = None
        for index, section in enumerate(
            self._applications[application_id]["sections"]
        ):
            if section["section_name"].lower() == section_name.lower():
                section_index = index
                self._applications[application_id]["sections"][
                    section_index
                ] = new_json
                # Update application statuses
                self._update_statuses(application_id)
        # Set last edited
        self._applications[application_id][
            "last_edited"
        ] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # IF section includes "your-project-name" field
        # THEN update application project name
        project_name = list(
            self._find_value_by_key(new_json, "your-project-name")
        )
        if len(project_name) == 1:
            self._applications[application_id]["project_name"] = project_name[
                0
            ]
        return self._applications[application_id]["sections"][section_index]

    def get_application(self, application_id: str):
        return self._applications.get(application_id)

    def get_applications(self):
        return [
            application
            for application_id, application in self._applications.items()
        ]

    @staticmethod
    def _set_attributes(
        account_id: str, fund_id: str, round_id: str, sections: List
    ) -> tuple:
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
                question.update({"status": "NOT STARTED"})
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
                        question["status"] = "COMPLETED"
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
                    section["status"] = "COMPLETED"
                elif question["status"] == "IN_PROGRESS":
                    section["status"] = "IN_PROGRESS"
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
        status_values = [
            section["status"] for section in application["sections"]
        ]
        if "IN_PROGRESS" in status_values:
            status = "IN_PROGRESS"
        elif "COMPLETED" in status_values:
            status = "COMPLETED"
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
