from api.namespace.applications.applications_ns import applications_ns
from api.namespace.applications.models.application import application_full
from api.namespace.applications.models.application import application_inbound
from api.namespace.applications.models.application import application_status
from api.namespace.applications.models.applications import applications_result
from database.store import APPLICATIONS
from flask import abort
from flask_restx import fields
from flask_restx import reqparse
from flask_restx import Resource


@applications_ns.route("/search")
class SearchApplications(Resource):
    """
    GET all relevant applications with endpoint '/search?{params}'
    """

    query_params_parser = reqparse.RequestParser()
    query_params_parser.add_argument(
        "id_contains", type=str, help="Application id contains string"
    )
    query_params_parser.add_argument(
        "fund_id", type=str, help="Application fund_id"
    )
    query_params_parser.add_argument(
        "order_by", type=str, help="Order results by parameter"
    )
    query_params_parser.add_argument(
        "order_rev",
        type=str,
        help=(
            "Order results by descending (default) or ascending (order_rev=1)"
        ),
    )
    query_params_parser.add_argument(
        "status_only", type=str, help="Only return results with given status"
    )
    query_params_parser.add_argument(
        "datetime_start",
        type=str,
        help="Only include results after this datetime",
    )
    query_params_parser.add_argument(
        "datetime_end",
        type=str,
        help="Only include results before this datetime",
    )

    @applications_ns.doc("get_applications", parser=query_params_parser)
    @applications_ns.marshal_with(applications_result, as_list=True, code=200)
    def get(self):
        args = self.query_params_parser.parse_args()
        response_headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": True,
        }
        return APPLICATIONS.search_applications(args), 200, response_headers


@applications_ns.route("", methods=["GET", "POST"])
class ApplicationCreate(Resource):
    """
    Create a new application
    """

    @applications_ns.doc("create_application")
    @applications_ns.expect(application_inbound)
    @applications_ns.marshal_with(application_full, code=201)
    def post(self):
        return APPLICATIONS.create_application(applications_ns.payload), 201


@applications_ns.route("/<application_id>", methods=["GET", "POST"])
class Application(Resource):
    """
    Operations on a single application
    """

    @applications_ns.doc("get_application")
    @applications_ns.marshal_with(application_full, code=200)
    def get(self, application_id):
        return APPLICATIONS.get_application(application_id), 200


@applications_ns.route("/<application_id>/status", methods=["GET", "PUT"])
class ApplicationStatus(Resource):
    """
    Operations on application assessment status
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

    @applications_ns.doc("get_application_status")
    @applications_ns.marshal_with(application_status, code=200)
    def get(self, application_id):
        status = APPLICATIONS.get_status(application_id)
        if not status:
            abort(404)
        return status

    @applications_ns.doc("put_status", parser=query_params_parser)
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
