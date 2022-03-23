from api.namespace.fund.data_store.store import APPLICATIONS
from api.namespace.fund.fund_ns import application_model_inbound
from api.namespace.fund.fund_ns import fund_ns
from flask_restx import reqparse
from flask_restx import Resource


@fund_ns.route("/status/<application_id>", methods=["GET"])
class ApplicationStatus(Resource):
    """Summary: Function is a get method which
    returns status of each question page from
    application with name/title of the question page.

    Args:
        application: Takes an application_id

    Returns:
        Status of a question from each page
    """

    status_params_parser = reqparse.RequestParser()
    status_params_parser.add_argument(
        "status",
        type=str,
        help="application status is set to NOT_STARTED  by default",
    )

    def get(self, application_id):
        application_status = APPLICATIONS.get_status(application_id)
        for application_id in application_status:
            for status in application_status.values():
                return {"Application id": application_id, "Questions": status}


@fund_ns.route("/status/<application_id>/<question_name>", methods=["PUT"])
class UpdateApplicationStatus(Resource):

    """_summary_:
        Function is a put method which
        updates the question status from
        "NOT STARTED" to "COMPLETED"
    Args:
        application_id (str): Takes an application and runs through
        get status function to validate the application id against
        the database.
        question_name (str): Takes an question name and runs through
        get status function to check the retrive the question
    Returns:
         returns updated status -> "COMPLETED"
    """

    def put(self, application_id, question_name):
        question_status = APPLICATIONS.update_question_status_to_COMPLETED(
            application_id=application_id, question_name=question_name
        )

        return {question_name: question_status}


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
