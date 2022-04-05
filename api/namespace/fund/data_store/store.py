"""
Data Access Object
A data access object (DAO) is a pattern that provides an abstract interface
to some type of database or other persistence mechanism.
"""
import datetime
import json
import uuid

from api.namespace.fund.data_store.data import initial_fund_store_application
from api.namespace.fund.data_store.data import initial_fund_store_state
from dateutil import parser as date_parser
from dateutil.tz import UTC
from slugify import slugify
from operator import itemgetter
from distutils.util import strtobool
from external_data.data import get_round


class ApplicationDataAccessObject(object):
    """
    return all funds (replace the date object with a string to send)
    """

    def __init__(self):
        self.counter = 0
        self.funds = initial_fund_store_state

    def get_funds(self):
        return json.loads(json.dumps(self.funds, default=str))

    @property
    def applications_index(self):
        applications = []
        for fund_name, fund_applications in self.funds.items():
            for fund_application in fund_applications:
                application_summary = {
                    "id": fund_application.get("id"),
                    "status": fund_application.get("status"),
                    "assessment_deadline": fund_application.get("assessment_deadline"),
                    "fund_id": fund_name,
                }
                applications.append(application_summary)
        return json.loads(json.dumps(applications, default=str))

    def create_application(self, application):
        fund_id = slugify(application["name"])
        return self.add_application(fund_id, application)

    def add_application(self, fund_id: str, application: dict):
        if fund_id not in self.funds:
            self.funds[fund_id] = []
        self.funds[fund_id].append(self.set_defaults(fund_id, application))
        return application

    @staticmethod
    def set_defaults(fund_id: str, application: dict):
        date_submitted = datetime.datetime.now(
            datetime.timezone.utc
        )
        round_id = application.get("round_id")
        fund_round = get_round(fund_id, round_id, date_submitted)

        application["date_submitted"] = date_submitted
        application["id"] = str(uuid.uuid4())  # cant be uuid in restx handler
        application["assessment_deadline"] = fund_round.assessment_deadline
        application["status"] = "NOT_STARTED"
        for question in application.get("questions"):
            question.update({"status": "NOT STARTED"})

        return application

    def get_status(self, application_id):
        """Summary:
            Function returns status of each question page from
            application with question page title/name.
        Args:
            application_id: Takes an application_id
        Returns:
            Status of a question from each page
        """
        for funds in self.funds.values():
            for fund in funds:
                if application_id == fund["id"]:
                    status = {
                        data.get("question"): data.get("status")
                        for data in fund.get("questions")
                    }
                    return status

    def update_status(
        self, application_id: str, question_name: str, new_status: str
    ) -> None:
        """_summary_:
            Function returns status of each question page from
            application with question page title/name.

        Args:
            application_id (str): Takes an application_id
            question_name (str): Takes an question name
            new_status (str): Takes a status name to be updated

        Returns:
            returns updated status.
        """

        for fund in self.funds.values():
            for application in fund:
                if application["id"] == application_id:
                    for question in application["questions"]:
                        if question["question"] == question_name:
                            question["status"] = new_status
                            return True
        return False

    def get_applications_for_fund(
        self, fund_name, datetime_start, datetime_end
    ):
        try:
            fund_data = self.funds[fund_name]
            applications_within_period = []
            if datetime_start and datetime_end:
                start = date_parser.parse(datetime_start).astimezone(UTC)
                end = date_parser.parse(datetime_end).astimezone(UTC)

                # compare period limits against application dates within fund
                for application in self.funds[fund_name]:
                    if (
                        start
                        <= application["date_submitted"].astimezone(UTC)
                        <= end
                    ):
                        applications_within_period.append(application)
                return json.loads(
                    json.dumps(applications_within_period, default=str)
                )
            else:
                return json.loads(json.dumps(fund_data, default=str))
        except KeyError:
            return f"Fund: {fund_name} not found.", 400

    def search_applications(self, params):
        """
        Returns a list of applications matching required params
        """
        matching_applications = []
        status_only = params.get("status_only")
        id_contains = params.get("id_contains")
        order_by = params.get("order_by", "id")
        order_rev = params.get("order_rev") or False
        try:
            order_rev = strtobool(order_rev)
        except ValueError:
            pass
        except AttributeError:
            pass

        for application in self.applications_index:
            match = True
            if status_only and \
                    status_only.replace(" ", "_").upper() != application.get("status"):
                match = False
            if id_contains and id_contains not in application.get("id"):
                match = False
            if match:
                matching_applications.append(application)

        if order_by and order_by in ["id", "status"]:
            matching_applications = sorted(
                matching_applications,
                key=itemgetter(order_by),
                reverse=order_rev)

        return matching_applications

    def get_application_by_id(self, fund_name, application_id):

        try:
            for application in self.funds[fund_name]:
                if application["id"] == application_id:
                    return json.loads(json.dumps(application, default=str))
            return (
                f"Application id: {application_id} not found in fund:"
                f" {fund_name}",
                400,
            )
        except KeyError:
            return f"Fund: {fund_name} not found.", 400

    def delete_application_by_id(self, fund_name, application_id):

        try:
            for application in self.funds[fund_name]:
                if application["id"] == application_id:
                    self.funds[fund_name].remove(application)
                    return f"{application_id} deleted", 204
            return (
                f"Application id: {application_id} not found in fund:"
                f" {fund_name}",
                400,
            )
        except KeyError:
            return f"Fund: {fund_name} not found.", 400

    def delete_all(self, delete_key):

        if delete_key == "positive-clear":
            self.funds = {}
        else:
            return "No key provided. Clear unsuccessful"


# An in memory data object instance


APPLICATIONS = ApplicationDataAccessObject()


APPLICATIONS.create_application(initial_fund_store_application)
