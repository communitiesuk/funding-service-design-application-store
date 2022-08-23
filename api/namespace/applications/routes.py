import uuid

from api.namespace.applications.applications_ns import applications_ns
from api.namespace.applications.helpers.helpers import ApplicationHelpers
from api.namespace.applications.models.application import application_outbound
from api.namespace.applications.models.application import application_result
from api.namespace.applications.models.application import application_status
from api.namespace.applications.models.application import create_application
from api.namespace.applications.models.form import form
from db.models.aggregate_functions import get_application_bundle_by_id
from db.models.aggregate_functions import submit_application
from db.models.aggregate_functions import update_form
from db.models.applications import ApplicationsMethods
from db.models.forms import FormsMethods
from flask import abort
from flask import current_app
from flask import request
from flask_restx import reqparse
from flask_restx import Resource
from sqlalchemy.orm.exc import NoResultFound


@applications_ns.route("")
class Applications(Resource):
    """
    GET all relevant applications with endpoint '?{params}'
    """
    query_params_parser = reqparse.RequestParser()
    query_params_parser.add_argument(
        "id_contains", type=str, help="Application id contains string"
    )
    query_params_parser.add_argument(
        "account_id", type=str, help="Application account_id"
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
    @applications_ns.marshal_with(application_result, as_list=True, code=200)
    def get(self):
        args = self.query_params_parser.parse_args()
        response_headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": True,
        }
        applications = ApplicationsMethods.search_applications(args)
        current_app.logger.info(
            "Returning application search results for search terms:"
            f" {args} with results of: {applications}"
        )
        return applications, 200, response_headers

    create_application_parser = reqparse.RequestParser()
    create_application_parser.add_argument("account_id", location="json")
    create_application_parser.add_argument("round_id", location="json")
    create_application_parser.add_argument("fund_id", location="json")

    @applications_ns.doc("post_application", parser=create_application_parser)
    @applications_ns.marshal_with(create_application, code=201)
    def post(self):
        args = self.create_application_parser.parse_args()
        account_id = args["account_id"]
        round_id = args["round_id"]
        fund_id = args["fund_id"]
        empty_forms = ApplicationHelpers.get_blank_forms(fund_id, round_id)
        application = ApplicationsMethods.create_application(
            account_id=account_id, fund_id=fund_id, round_id=round_id
        )
        FormsMethods.add_new_forms(
            forms=empty_forms, application_id=application.id
        )
        return application, 201


@applications_ns.route("/forms", methods=["PUT"])
class Form(Resource):

    put_form_parser = reqparse.RequestParser()
    put_form_parser.add_argument("name", location="json")

    @applications_ns.doc("put_form", methods=["PUT"], parser=put_form_parser)
    @applications_ns.marshal_with(form, code=201)
    def put(self):
        request_json = request.get_json(force=True)

        form_dict = {
            "application_id": request_json["metadata"]["application_id"],
            "form_name": request_json["metadata"].get("form_name"),
            "question_json": request_json["questions"],
        }

        try:
            updated_form = update_form(**form_dict)

            return updated_form, 201

        except NoResultFound as e:

            abort(404, f"No matching application form found : {e}")


@applications_ns.route("/<application_id>/submit")
class SubmitApplication(Resource):
    @applications_ns.doc("submit_application")
    def post(self, application_id):
        try:
            return_dict = submit_application(application_id)
            return return_dict, 201
        except KeyError:
            return "", 404


@applications_ns.route("/<application_id>")
class GetApplication(Resource):
    @applications_ns.doc("get_application")
    @applications_ns.marshal_with(application_outbound, code=201)
    def get(self, application_id):
        try:
            return_dict = get_application_bundle_by_id(
                uuid.UUID(application_id)
            )
            return return_dict, 200
        except NoResultFound:
            return "", 404


@applications_ns.route("/<application_id>/status")
class ApplicationStatus(Resource):
    """
    Operations on application assessment status
    """

    @applications_ns.doc("get_application_status")
    @applications_ns.marshal_with(application_status, code=200)
    def get(self, application_id):
        application = ApplicationsMethods.get_application_by_id(application_id)
        if not application:
            abort(404)
        return application.as_dict()
