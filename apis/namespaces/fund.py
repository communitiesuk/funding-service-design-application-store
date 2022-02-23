from flask_restx import Namespace, Resource, fields, reqparse
from slugify import slugify
import datetime
from dateutil import parser
import uuid
import json

# Set up namespace (acts as a 'mini' api)
api = Namespace("fund", description="application operations")

# create a data model
applicationModel = api.model('application', {
    'name': fields.String(required=True, description='Required: The name of the fund.'),
    'questions': fields.String(required=True, description='Required: The payload of application questions and answers.')
})


# Data Access Object
# A data access object (DAO) is a pattern that provides
# an abstract interface to some type of database or other persistence mechanism.

class applicationDAO(object):
    def __init__(self):
        self.counter = 0
        self.funds = {}

    def get_funds(self):
        # return all funds (have to replace the date object with a string to send)
        return json.loads(json.dumps(self.funds, default=str))

    def create_application(self, application):
        application_fund_name = slugify(application['name'])
        application_id = str(uuid.uuid4())  # cant be uuid for restx handler
        # create timestamp
        current_time = datetime.datetime.now(datetime.timezone.utc)
        application['date_submitted'] = current_time

        if application_fund_name not in self.funds:
            # create a new fund entry
            self.funds[application_fund_name] = {}

        # place application within the fund
        try:
            # allow custom ids if 'id' is provided in payload (allows testing)
            self.funds[application_fund_name][application['id']] = application
            return self.funds[application_fund_name][application['id']]
        except:
            self.funds[application_fund_name][application_id] = application
            return self.funds[application_fund_name][application_id]


    def get_applications_for_fund(self, fund_name, datetime_start, datetime_end):
        fund_data = self.funds[fund_name]
        applications_within_period = {}
        if datetime_start and datetime_end:
            # convert string dates into datetimes
            start = parser.parse(datetime_start)
            end = parser.parse(datetime_end)

            # compare period limits against application dates within fund
            for application in fund_data:
                data = fund_data[application]
                time = parser.parse(data['date_submitted'])
                if time > start and time < end:
                    applications_within_period[application] = data
            return json.loads(json.dumps(applications_within_period, default=str))
        else:
            return json.loads(json.dumps(fund_data, default=str))


    def get_application_by_id(self, fund_name, application_id):
        return self.funds[fund_name][application_id]


# In memory data object instance
DAO = applicationDAO()

DAO.create_application({
    'name': 'Test Fund',
    'questions': {"test": "data"}
})


# GET ALL FUNDS
@api.route('/')
class Fund(Resource):
    @api.doc('list_funds')
    def get(self):
        return DAO.get_funds()


# CREATE A NEW APPLICATION
@api.route('/new_application')
class NewApplication(Resource):
    @api.doc('create_application')
    @api.expect(applicationModel)
    @api.marshal_with(applicationModel, code=201)
    def post(self):
        return DAO.create_application(api.payload), 201


# GET ALL APPLICATIONS FOR A FUND
@api.route('/<string:fund_name>/applications')
class Application(Resource):
    # For query parameters
    query_params_parser = reqparse.RequestParser()
    query_params_parser.add_argument('datetime_start', type=str, help='Lower bound datetime of the period to search applications (optional)')
    query_params_parser.add_argument('datetime_end', type=str, help='Upper bound datetime of the period to search applications (optional)')

    @api.doc('get_applications', parser=query_params_parser)
    def get(self, fund_name):
        args = self.query_params_parser.parse_args()
        datetime_start = args['datetime_start']
        datetime_end = args['datetime_start']
        return DAO.get_applications_for_fund(fund_name, datetime_start, datetime_end)


# GET AN APPLICATION FOR A FUND WITH ID {?}
@api.route('/<string:fund_name>')
class Application(Resource):
    # For query parameters
    query_params_parser = reqparse.RequestParser()
    query_params_parser.add_argument('application_id', type=str, help='Application id')

    @api.doc('get_applications', parser=query_params_parser)
    def get(self, fund_name):
        args = self.query_params_parser.parse_args()
        application_id = args['application_id']
        return DAO.get_application_by_id(fund_name, application_id)
