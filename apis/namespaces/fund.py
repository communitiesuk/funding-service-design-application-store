from flask_restx import Namespace, Resource, fields, reqparse
from slugify import slugify
import datetime
from dateutil import parser
import uuid
import json

# Set up namespace (acts as a 'mini' api)
api = Namespace("fund", description="application operations")

arg_parser = reqparse.RequestParser()
arg_parser.add_argument('period_start', type=str, help='period start')
arg_parser.add_argument('period_end', type=str, help='period end')
arg_parser.add_argument('application_id', type=str, help='application id')

# create a data model
applicationModel = api.model('application', {
    'id': fields.Integer(required=False),
    'name': fields.String(required=True, description='The name of the fund.'),
    'questions': fields.String(required=True, description='The payload of application questions.'),
    'date_submitted': fields.DateTime(
        required=False,
        description='The time the application was received by the application store.'
    )
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


def get_applications_for_fund(self, fund_name, period_start, period_end):
    fund_data = self.funds[fund_name]
    applications_within_period = {}

    if period_start and period_end:
        # convert string dates into datetimes
        start = parser.parse(period_start)
        end = parser.parse(period_end)

        # compare period limits against application dates within fund
        for application in fund_data:
            data = fund_data[application]
            time = parser.parse(data['date_submitted'])
            if time > start and time < end:
                applications_within_period[application] = data
        return applications_within_period
    else:
        return fund_data


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
    @api.doc('get_applications', parser=arg_parser)
    def get(self, fund_name):
        args = arg_parser.parse_args()
        period_start = args['period_start']
        period_end = args['period_start']
        return DAO.get_applications_for_fund(fund_name, period_start, period_end)


# GET AN APPLICATION FOR A FUND WITH ID {?}
@api.route('/<string:fund_name>')
class Application(Resource):
    @api.doc('get_applications', parser=arg_parser)
    def get(self, fund_name):
        args = arg_parser.parse_args()
        application_id = args['application_id']
        return DAO.get_application_by_id(fund_name, application_id)
