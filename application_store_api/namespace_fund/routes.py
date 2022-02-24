from flask_restx import Resource, reqparse
from application_store_api.namespace_fund.store import APPLICATIONS
from application_store_api.namespace_fund.api import fund_ns, applicationModel

# GET/DELETE All funds
@fund_ns.route('/')
class Fund(Resource):
    # For query parameters
    query_params_parser = reqparse.RequestParser()
    query_params_parser.add_argument('delete_key', type=str, help='key to clear data store')

    @fund_ns.doc('list_funds')
    def get(self):
        return APPLICATIONS.get_funds()

    # Remove once data store is persisted outside of application memory
    @fund_ns.doc('list_funds')
    def delete(self):
        args = self.query_params_parser.parse_args()
        delete_key = args['delete_key']
        return APPLICATIONS.delete_all(delete_key)


# POST a new application
@fund_ns.route('/new_application')
class NewApplication(Resource):
    @fund_ns.doc('create_application')
    @fund_ns.expect(applicationModel)
    @fund_ns.marshal_with(applicationModel, code=201)
    def post(self):
        return APPLICATIONS.create_application(fund_ns.payload), 201


# GET all applications for a fund 'fund/fund-name' or a specific application fund/fund-name?application_id={Id}
@fund_ns.route('/<string:slugify_fund_name>')
class Application(Resource):
    # For query parameters
    query_params_parser = reqparse.RequestParser()
    query_params_parser.add_argument('application_id', type=str, help='Application id')
    query_params_parser.add_argument('datetime_start', type=str, help='Lower bound datetime of the period to search applications (optional)')
    query_params_parser.add_argument('datetime_end', type=str, help='Upper bound datetime of the period to search applications (optional)')

    @fund_ns.doc('get_applications', parser=query_params_parser)
    def get(self, slugify_fund_name):
        args = self.query_params_parser.parse_args()

        datetime_end = args['datetime_end']
        datetime_start = args['datetime_start']
        application_id = args['application_id']
        if application_id:
            return APPLICATIONS.get_application_by_id(slugify_fund_name, application_id)
        else:
            return APPLICATIONS.get_applications_for_fund(slugify_fund_name, datetime_start, datetime_end)


    @fund_ns.doc('delete_application', parser=query_params_parser)
    @fund_ns.response(204, 'application deleted')
    def delete(self, slugify_fund_name):
        args = self.query_params_parser.parse_args()
        application_id = args['application_id']
        return APPLICATIONS.delete_application_by_id(slugify_fund_name, application_id)
