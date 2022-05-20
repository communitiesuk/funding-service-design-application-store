from api.namespace.applications.applications_ns import applications_ns
from api.namespace.applications.models.application import application_full
from api.namespace.applications.models.application import application_result
from api.namespace.applications.models.application import application_status
from api.namespace.applications.models.section import section
from database.store import APPLICATIONS
from flask import abort
from flask import request
from flask_restx import reqparse
from flask_restx import Resource


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
        return APPLICATIONS.search_applications(args), 200, response_headers

    create_application_parser = reqparse.RequestParser()
    create_application_parser.add_argument("account_id", location="json")
    create_application_parser.add_argument("round_id", location="json")
    create_application_parser.add_argument("fund_id", location="json")

    @applications_ns.doc("post_application", parser=create_application_parser)
    @applications_ns.marshal_with(application_full, code=201)
    def post(self):
        args = self.create_application_parser.parse_args()
        account_id = args["account_id"]
        round_id = args["round_id"]
        fund_id = args["fund_id"]
        macro_dict = APPLICATIONS.create_application(
            account_id=account_id, fund_id=fund_id, round_id=round_id
        )
        return macro_dict, 201


@applications_ns.route("/sections")
class Section(Resource):

    put_section_parser = reqparse.RequestParser()
    put_section_parser.add_argument("name", location="json")

    @applications_ns.doc(
        "put_section", methods=["PUT"], parser=put_section_parser
    )
    @applications_ns.marshal_with(section, code=201)
    def put(self):
        request_json = request.get_json(force=True)
        section_name = request_json["name"]
        section_questions = request_json["questions"]
        section_metadata = request_json["metadata"]
        application_id = request_json["metadata"]["application_id"]

        section_dict = {
            "questions": section_questions,
            "section_name": section_name,
            "metadata": section_metadata,
        }

        updated_section = APPLICATIONS.put_section(
            application_id, section_name, section_dict
        )

        return updated_section, 201


@applications_ns.route("/<application_id>/submit")
class SubmitApplication(Resource):
    @applications_ns.doc("submit_application")
    def post(self, application_id):
        try:
            return_dict = APPLICATIONS.submit_application(application_id)
            return return_dict, 201
        except KeyError:
            return "", 404


@applications_ns.route("/<application_id>")
class GetApplication(Resource):
    @applications_ns.doc("get_application")
    @applications_ns.marshal_with(application_full, code=201)
    def get(self, application_id):
        try:
            return_dict = APPLICATIONS.get_application(application_id)
            return return_dict, 200
        except KeyError:
            return "", 404


@applications_ns.route("/<application_id>/status")
class ApplicationStatus(Resource):
    """
    Operations on application assessment status
    """

    @applications_ns.doc("get_application_status")
    @applications_ns.marshal_with(application_status, code=200)
    def get(self, application_id):
        status = APPLICATIONS.get_status(application_id)
        if not status:
            abort(404)
        return status
