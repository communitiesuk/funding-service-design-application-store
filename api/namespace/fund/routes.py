from api.namespace.fund.data_store.store import APPLICATIONS
from api.namespace.fund.fund_ns import application_model_inbound
from api.namespace.fund.fund_ns import fund_ns
from flask_restx import reqparse
from flask_restx import Resource


@fund_ns.route("/status/<application_id>", methods=["GET", "PUT"])
class ApplicationStatus(Resource):
    """Summary: Function is a get method which
    returns status of each question page from
    application with name/title of the question page.

    Args:
        application: Takes an application_id

    Returns:
        Status of a question from each page
    """

    query_params_parser = reqparse.RequestParser()
    query_params_parser.add_argument(
        "new_status", type=str, help="What the status will be changed to."
    )
    query_params_parser.add_argument(
        "question_name",
        type=str,
        help="The name of the question to be accessed.",
    )

    def get(self, application_id):
        application_status = APPLICATIONS.get_status(application_id)
        for application_id in application_status:
            for status in application_status.values():
                return {"Application id": application_id, "Questions": status}

    @fund_ns.doc("put_status", parser=query_params_parser)
    def put(self, application_id):

        args = self.query_params_parser.parse_args()

        question_name = args["question_name"]

        new_status = args["new_status"]

        status_update = APPLICATIONS.update_status(
            application_id, question_name, new_status
        )

        if status_update:
            return 200
        else:
            return 404


@fund_ns.route("/all_funds")
class Fund(Resource):
    """
    GET/DELETE all funds
    """

    query_params_parser = reqparse.RequestParser()
    query_params_parser.add_argument(
        "delete_key", type=str, help="key to clear data store"
    )

    @fund_ns.doc("list_funds")
    def get(self):
        return APPLICATIONS.get_funds()


@fund_ns.route("/new_application")
class NewApplication(Resource):
    """
    POST a new application
    """

    @fund_ns.doc("create_application")
    @fund_ns.expect(application_model_inbound)
    @fund_ns.marshal_with(application_model_inbound, code=201)
    def post(self):
        return APPLICATIONS.create_application(fund_ns.payload), 201


@fund_ns.route("/<string:slugify_fund_name>")
class Application(Resource):
    """
    GET all applications for a fund 'fund/{fund-name}'
    OR GET all applications for a fund in a specified period
    'fund/{fund-name}/<date range parameters>'
    OR GET a specific application fund/fund-name?application_id={Id}
    """

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
