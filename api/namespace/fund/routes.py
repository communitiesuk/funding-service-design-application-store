from api.namespace.fund.data_store.store import APPLICATIONS
from api.namespace.fund.fund_ns import application_model_inbound
from api.namespace.fund.fund_ns import fund_ns
from flask_restx import reqparse
from flask_restx import Resource

"""
GET/DELETE all funds
"""


@fund_ns.route("/all_funds")
class Fund(Resource):
    query_params_parser = reqparse.RequestParser()
    query_params_parser.add_argument(
        "delete_key", type=str, help="key to clear data store"
    )

    @fund_ns.doc("list_funds")
    def get(self):
        return APPLICATIONS.get_funds()


"""
POST a new application
"""


@fund_ns.route("/new_application")
class NewApplication(Resource):
    @fund_ns.doc("create_application")
    @fund_ns.expect(application_model_inbound)
    @fund_ns.marshal_with(application_model_inbound, code=201)
    def post(self):
        return APPLICATIONS.create_application(fund_ns.payload), 201


"""
GET all applications for a fund 'fund/{fund-name}'
OR GET all applications for a fund in a specified period
'fund/{fund-name}/<date range parameters>'
OR GET a specific application fund/fund-name?application_id={Id}
"""


@fund_ns.route("/<string:slugify_fund_name>")
class Application(Resource):
    query_params_parser = reqparse.RequestParser()
    query_params_parser.add_argument(
        "application_id", type=str, help="Application id"
    )

    @fund_ns.doc("get_applications", parser=query_params_parser)
    def get(self, slugify_fund_name):
        args = self.query_params_parser.parse_args()

        application_id = args["application_id"]
        if application_id:
            return APPLICATIONS.get_application_by_id(
                slugify_fund_name, application_id
            )
        else:
            return APPLICATIONS.get_applications_for_fund(slugify_fund_name)

    @fund_ns.doc("delete_application", parser=query_params_parser)
    @fund_ns.response(204, "application deleted")
    def delete(self, slugify_fund_name):
        args = self.query_params_parser.parse_args()
        application_id = args["application_id"]
        return APPLICATIONS.delete_application_by_id(
            slugify_fund_name, application_id
        )
