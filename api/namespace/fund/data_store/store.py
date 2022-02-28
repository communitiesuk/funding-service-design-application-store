import datetime
import json
import uuid

from api.namespace.fund.data_store.data import initial_fund_store_application
from api.namespace.fund.data_store.data import initial_fund_store_state
from slugify import slugify

"""
Data Access Object
A data access object (DAO) is a pattern that provides an abstract interface
to some type of database or other persistence mechanism.
"""


class ApplicationDataAccessObject(object):
    def __init__(self):
        self.counter = 0
        self.funds = initial_fund_store_state

    """
        return all funds (replace the date object with a string to send)
    """

    def get_funds(self):
        return json.loads(json.dumps(self.funds, default=str))

    def create_application(self, application):
        fund_name = slugify(application["name"])
        application["date_submitted"] = datetime.datetime.now(
            datetime.timezone.utc
        )
        application["id"] = str(uuid.uuid4())  # cant be uuid in restx handler

        if fund_name not in self.funds:
            self.funds[fund_name] = []

        self.funds[fund_name].append(application)
        return application

    def get_applications_for_fund(self, fund_name):
        try:
            fund_data = self.funds[fund_name]
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


"""
An in memory data object instance
"""

APPLICATIONS = ApplicationDataAccessObject()

APPLICATIONS.create_application(initial_fund_store_application)
