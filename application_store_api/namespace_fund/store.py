from slugify import slugify
import datetime
from dateutil import parser as date_parser
from dateutil.tz import UTC
import uuid
import json

"""
Data Access Object
A data access object (DAO) is a pattern that provides an abstract interface 
to some type of database or other persistence mechanism.
"""


class applicationDAO(object):
    def __init__(self):
        self.counter = 0
        self.funds = {
            "slugified_test_fund_name": [
                {
                    "id": "uuidv4",
                    "name": "Test Fund Name",
                    "questions": {
                        "q1": "a1"
                    },
                    "date_submitted": date_parser.parse("2021-12-25 00:00:00")
                }
            ]
        }

    def get_funds(self):
        # return all funds (have to replace the date object with a string to send)
        return json.loads(json.dumps(self.funds, default=str))

    def create_application(self, application):
        application_fund_name = slugify(application['name'])
        application_id = str(uuid.uuid4())  # cant be uuid in restx handler
        current_time = datetime.datetime.now(datetime.timezone.utc)
        application['date_submitted'] = current_time
        application['id'] = application_id

        if application_fund_name not in self.funds:
            # create a new fund entry
            self.funds[application_fund_name] = []

        # place application within the fund
        self.funds[application_fund_name].append(application)
        return application

    def get_applications_for_fund(self, fund_name, datetime_start, datetime_end):
        fund_data = self.funds[fund_name]
        applications_within_period = []
        if datetime_start and datetime_end:
            # convert string dates into datetimes
            start = date_parser.parse(datetime_start).astimezone(UTC)
            end = date_parser.parse(datetime_end).astimezone(UTC)

            # compare period limits against application dates within fund
            for application in self.funds[fund_name]:
                if start < application['date_submitted'].astimezone(UTC) < end:
                    applications_within_period.append(application)
            return json.loads(json.dumps(applications_within_period, default=str))
        else:
            return json.loads(json.dumps(fund_data, default=str))

    def get_application_by_id(self, fund_name, application_id):
        try:
            for application in self.funds[fund_name]:
                if application['id'] == application_id:
                    return json.loads(json.dumps(application, default=str))
            return f"Application id: {application_id} not found in fund: {fund_name}", 400
        except:
            return f"Fund: {fund_name} not found.", 400

    def delete_application_by_id(self, fund_name, application_id):
        try:
            for application in self.funds[fund_name]:
                if application['id'] == application_id:
                    self.funds[fund_name].remove(application)
                    return f"{application_id} deleted", 204
            return f"Application id: {application_id} not found in fund: {fund_name}", 400
        except:
            return f"Fund: {fund_name} not found.", 400


def delete_all(self, delete_key):
    if delete_key == 'positive-clear':
        self.funds = {}
    else:
        return 'No key provided. Clear unsuccessful'


# Sample data
sample_application_data = [
    #     {
    #     'name': 'Test Fund',
    #     'questions': {"test": "data"}
    # }
]

# In memory data object instance
APPLICATIONS = applicationDAO()

for application in sample_application_data:
    APPLICATIONS.create_application(application)
