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
        self.funds = {}

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
            self.funds[application_fund_name] = {}

        # place application within the fund
        self.funds[application_fund_name][application_id] = application
        return self.funds[application_fund_name][application_id]

    def get_applications_for_fund(self, fund_name, datetime_start, datetime_end):
        fund_data = self.funds[fund_name]
        applications_within_period = {}
        if datetime_start and datetime_end:
            # convert string dates into datetimes
            start = date_parser.parse(datetime_start).astimezone(UTC)
            end = date_parser.parse(datetime_end).astimezone(UTC)

            # compare period limits against application dates within fund
            for applicationId in fund_data:
                application_data = fund_data[applicationId]
                application_date = application_data['date_submitted'].astimezone(UTC)
                if start <= application_date <= end:
                    applications_within_period[applicationId] = application_data
            return json.loads(json.dumps(applications_within_period, default=str))
        else:
            return json.loads(json.dumps(fund_data, default=str))

    def get_application_by_id(self, fund_name, application_id):
        application_data = self.funds[fund_name][application_id]
        return json.loads(json.dumps(application_data, default=str))

    def delete_application_by_id(self, fund_name, application_id):
        print('ere')
        fund = self.funds[fund_name]
        del fund[application_id]
        print('del')

    def delete_all(self, delete_key):
        if delete_key == 'positive-clear':
            self.funds = {}
        else:
            return 'No key provided. Clear unsuccessful'
