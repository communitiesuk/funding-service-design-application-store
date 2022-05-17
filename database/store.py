import datetime
import uuid
from operator import itemgetter

from database.initial_data import initial_application
from database.initial_data import initial_application_store_state
from dateutil import parser as date_parser
from dateutil.tz import UTC
from external_data.data import get_round
from slugify import slugify


class ApplicationDataAccessObject(object):
    """
    A data interface to our currently in-memory data store
    """

    def __init__(self):
        self._applications: dict = initial_application_store_state
        self._macro_applications: dict = {}

    @property
    def applications_index(self) -> dict:
        applications = {}
        for application_id, application in self._applications.items():
            application_summary = {
                "id": application.get("id"),
                "status": application.get("status"),
                "fund_id": application.get("fund_id"),
                "round_id": application.get("round_id"),
                "date_submitted": application.get("date_submitted"),
                "assessment_deadline": application.get("assessment_deadline"),
            }
            applications.update({application.get("id"): application_summary})
        return applications

    def create_application(self, application):
        fund_id = slugify(application["name"])
        application_id, new_application = self.set_attributes(
            fund_id, application
        )
        self._applications.update({application_id: new_application})
        return new_application

    def create_macro_application(self, account_id, fund_id, round_id):

        macro_application_id = str(uuid.uuid4())

        macro_application_dict = {
            "application_id": macro_application_id,
            "account_id": account_id,
            "round_id": round_id,
            "fund_id": fund_id,
            "sections": [],
            "submission_stamp": None,
        }

        self._macro_applications[macro_application_id] = macro_application_dict

        return macro_application_dict

    def get_macro_application(self, macro_id):
        return self._macro_applications.get(macro_id)

    def submit_macro_application(self, application_id):
        self._macro_applications[application_id]["submission_stamp"] = str(
            datetime.datetime.now(datetime.timezone.utc)
        )
        return self._macro_applications[application_id]

    def get_section(self, application_id, section_name):
        return self._macro_applications[application_id]["sections"][
            section_name
        ]

    def put_post_section(self, application_id, section_name, new_json):
        self._macro_applications[application_id]["sections"][section_name].update(new_json)
        return self._macro_applications[application_id]["sections"][section_name]

    def get_application(self, application_id: str):
        return self._applications.get(application_id)

    @staticmethod
    def set_attributes(fund_id: str, application_raw: dict) -> tuple:
        application = application_raw
        # Remove name property (replace with fund_id)
        application.pop("name")
        date_submitted = datetime.datetime.now(datetime.timezone.utc)
        round_id = application_raw.get("round_id")  # Get round_id if set
        fund_round = get_round(fund_id, round_id, date_submitted)

        application["id"] = str(uuid.uuid4())  # cant be uuid in restx handler
        application["status"] = "NOT_STARTED"
        application["fund_id"] = fund_id
        application["round_id"] = fund_round.identifier
        application["date_submitted"] = date_submitted
        application["assessment_deadline"] = fund_round.assessment_deadline
        for question in application.get("questions"):
            question.update({"status": "NOT STARTED"})
        return application["id"], application

    def get_status(self, application_id):
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
            questions = []
            for question in self._applications[application_id].get(
                "questions"
            ):
                questions.append(
                    {
                        "question": question.get("question"),
                        "status": question.get("status"),
                    }
                )
            application_summary.update({"questions": questions})
            return application_summary

    def update_status(
        self, application_id: str, question_name: str, new_status: str
    ) -> dict or False:
        """
        Summary:
            Given application_id, update status of question_name to new_status
        Args:
            application_id (str): Takes an application_id
            question_name (str): Takes an question name
            new_status (str): Takes a status name to be updated

        Returns: status confirmation dict or False.
        """
        application = self._applications.get(application_id)
        for question in application["questions"]:
            if question["question"] == question_name:
                question["status"] = new_status
                return {question_name: new_status}
        return False

    def search_applications(self, params):
        """
        Returns a list of applications matching required params
        """
        matching_applications = []
        datetime_start = params.get("datetime_start")
        datetime_end = params.get("datetime_end")
        fund_id = params.get("fund_id")
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

        if order_by and order_by in ["id", "status", "assessment_deadline"]:
            matching_applications = sorted(
                matching_applications,
                key=itemgetter(order_by),
                reverse=order_rev,
            )

        return matching_applications


# An in memory data object instance


APPLICATIONS = ApplicationDataAccessObject()


APPLICATIONS.create_application(initial_application)
