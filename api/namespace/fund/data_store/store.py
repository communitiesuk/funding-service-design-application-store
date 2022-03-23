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


class ApplicationDataAccessObject(object):
    """
    return all funds (replace the date object with a string to send)
    """

    def __init__(self):
        self.counter = 0
        self.funds = initial_fund_store_state

    def create_status(self, application):
        """Summary:
            Function create status & set to NOT_STARTED
            by deafult to each question page
        Args:
            application: Takes an application/fund
        """
        for question in application["questions"]:
            question["status"] = "NOT STARTED"

    def get_funds(self):
        return json.loads(json.dumps(self.funds, default=str))

    def get_status(self, application_id):
        """Summary:
            Function returns status of each question page from
            application with question page title/name.
        Args:
            application: Takes an application_id
        Returns:
            Status of a question from each page
        """
        status = {}
        for funds in self.funds.values():
            for fund in funds:
                if application_id == fund["id"]:
                    status[application_id] = {
                        data.get("question"): data.get("status")
                        for data in fund.get("questions")
                    }
        return status

    def update_question_status_to_COMPLETED(
        self, application_id, question_name
    ):
        """_summary_:
            Function updates the question status from
            "NOT STARTED" to "COMPLETED"
        Args:
            application_id (str): Takes an application and runs through
            get status function to validate the application id against
            the database.
            question_name (str): Takes an question name and runs through
            get status function to check the retrive the question data.
        Returns:
            _type_: returns updated status -> "COMPLETED"
        """

        status = ""
        application_data = self.get_status(application_id)
        if application_id in application_data:
            for questions in application_data.values():
                if question_name in questions:
                    status += str(questions[question_name])
                else:
                    return f"Question name '{question_name}' does not exist"

        else:
            return f"Application id '{application_id}' does not exist"

        status = "COMPLETED"
        return status

    def create_application(self, application):
        fund_name = slugify(application["name"])
        application["date_submitted"] = datetime.datetime.now(
            datetime.timezone.utc
        )
        application["id"] = str(uuid.uuid4())  # cant be uuid in restx handler

        if fund_name not in self.funds:
            self.funds[fund_name] = []
        self.funds[fund_name].append(application)
        self.create_status(application)
        return application

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
