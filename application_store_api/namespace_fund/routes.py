from application_store_api.namespace_fund.data_store.store import APPLICATIONS
from application_store_api.namespace_fund.fund_ns import (
    application_model_inbound,
)
from application_store_api.namespace_fund.fund_ns import fund_ns
from flask_restx import reqparse
from flask_restx import Resource


# GET/DELETE all funds
@fund_ns.route("/all_funds")
class Fund(Resource):
    query_params_parser = reqparse.RequestParser()
    query_params_parser.add_argument(
        "delete_key", type=str, help="key to clear data store"
    )

    @fund_ns.doc("list_funds")
    def get(self):
        return APPLICATIONS.get_funds()

    # Remove once data store is persisted outside of application memory
    @fund_ns.doc("list_funds", parser=query_params_parser)
    def delete(self):
        args = self.query_params_parser.parse_args()
        delete_key = args["delete_key"]
        return APPLICATIONS.delete_all(delete_key)


# POST a new application
@fund_ns.route("/new_application")
class NewApplication(Resource):
    @fund_ns.doc("create_application")
    @fund_ns.expect(application_model_inbound)
    @fund_ns.marshal_with(application_model_inbound, code=201)
    def post(self):
        return APPLICATIONS.create_application(fund_ns.payload), 201


"""
GET all applications for a fund 'fund/fund-name'
OR GET all applications for a fund in a specified period
'fund/fund-name/<date range parameters>'
OR GET a specific application fund/fund-name?application_id={Id}
"""


@fund_ns.route("/<string:slugify_fund_name>")
class Application(Resource):
    query_params_parser = reqparse.RequestParser()
    query_params_parser.add_argument(
        "application_id", type=str, help="Application id"
    )
    query_params_parser.add_argument(
        "datetime_start",
        type=str,
        help=(
            "When an application_id has not been provided. Lower bound"
            " datetime of a period to search all of the applications within a"
            " specified fund (optional)"
        ),
    )
    query_params_parser.add_argument(
        "datetime_end",
        type=str,
        help=(
            "When an application_id has not been provided. Upper bound"
            " datetime of a period to search all of the applications within a"
            " specified fund (optional)"
        ),
    )

    @fund_ns.doc("get_applications", parser=query_params_parser)
    def get(self, slugify_fund_name):
        args = self.query_params_parser.parse_args()

        datetime_end = args["datetime_end"]
        datetime_start = args["datetime_start"]
        application_id = args["application_id"]
        if application_id:
            return APPLICATIONS.get_application_by_id(
                slugify_fund_name, application_id
            )
        else:
            return APPLICATIONS.get_applications_for_fund(
                slugify_fund_name, datetime_start, datetime_end
            )

    @fund_ns.doc("delete_application", parser=query_params_parser)
    @fund_ns.response(204, "application deleted")
    def delete(self, slugify_fund_name):
        args = self.query_params_parser.parse_args()
        application_id = args["application_id"]
        return APPLICATIONS.delete_application_by_id(
            slugify_fund_name, application_id
        )
