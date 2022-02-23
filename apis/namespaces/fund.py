from flask_restx import Namespace, Resource, reqparse, fields
from apis.data.applications import applicationDAO
from apis.data.data_models import questions

# Set up namespace (acts as a 'mini' api)
api = Namespace("fund", description="application operations")

# Set up data models
questionsModel = api.model('questions', questions)
applicationModel = api.model('application', {
    'name': fields.String(required=True, description='Required: The name of the fund.'),
    'questions': fields.Nested(
        questionsModel,
        required=True,
        description='Required: The payload of application questions and answers.'
    )
})

# In memory data object instance
DAO = applicationDAO()
DAO.create_application({
    'name': 'Test Fund',
    'questions': {"test": "data"}
})

# GET/DELETE All funds
@api.route('/')
class Fund(Resource):
    # For query parameters
    query_params_parser = reqparse.RequestParser()
    query_params_parser.add_argument('delete_key', type=str, help='key to clear data store')

    @api.doc('list_funds')
    def get(self):
        return DAO.get_funds()

    # Remove once data store is persisted outside of application memory
    @api.doc('list_funds')
    def delete(self):
        args = self.query_params_parser.parse_args()
        delete_key = args['delete_key']
        return DAO.delete_all(delete_key)


# Create a new application
@api.route('/new_application')
class NewApplication(Resource):
    @api.doc('create_application')
    @api.expect(applicationModel)
    @api.marshal_with(applicationModel, code=201)
    def post(self):
        return DAO.create_application(api.payload), 201


# Get all applications for a fund
@api.route('/<string:slugify_fund_name>/applications')
class Application(Resource):
    # For query parameters
    query_params_parser = reqparse.RequestParser()
    query_params_parser.add_argument('datetime_start', type=str, help='Lower bound datetime of the period to search applications (optional)')
    query_params_parser.add_argument('datetime_end', type=str, help='Upper bound datetime of the period to search applications (optional)')

    @api.doc('get_applications', parser=query_params_parser)
    def get(self, slugify_fund_name):
        args = self.query_params_parser.parse_args()
        datetime_start = args['datetime_start']
        datetime_end = args['datetime_end']
        return DAO.get_applications_for_fund(slugify_fund_name, datetime_start, datetime_end)


# Get an application with {Id}
@api.route('/<string:slugify_fund_name>')
class Application(Resource):
    # For query parameters
    query_params_parser = reqparse.RequestParser()
    query_params_parser.add_argument('application_id', type=str, help='Application id')

    @api.doc('get_applications', parser=query_params_parser)
    def get(self, slugify_fund_name):
        args = self.query_params_parser.parse_args()
        application_id = args['application_id']
        return DAO.get_application_by_id(slugify_fund_name, application_id)

    @api.doc('delete_application', parser=query_params_parser)
    @api.response(204, 'application deleted')
    def delete(self, slugify_fund_name):
        args = self.query_params_parser.parse_args()
        application_id = args['application_id']
        return DAO.delete_application_by_id(slugify_fund_name, application_id), 204
