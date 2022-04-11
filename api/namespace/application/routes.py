from database.store import APPLICATIONS
from api.namespace.application.models.application import application_inbound
from api.namespace.application.models.application import application_full
from api.namespace.application.models.application import application_status
from api.namespace.application.application_ns import application_ns
from flask import abort
from flask_restx import reqparse
from flask_restx import Resource


@application_ns.route("", methods=["GET", "POST"])
class ApplicationCreate(Resource):
    """
    Create a new application
    """

    @application_ns.doc("create_application")
    @application_ns.expect(application_inbound)
    @application_ns.marshal_with(application_full, code=201)
    def post(self):
        return APPLICATIONS.create_application(application_ns.payload), 201


@application_ns.route("/<application_id>", methods=["GET", "POST"])
class Application(Resource):
    """
    Operations on a single application
    """

    @application_ns.doc("get_application")
    @application_ns.marshal_with(application_full, code=200)
    def get(self, application_id):
        return APPLICATIONS.get_application(application_id), 200


@application_ns.route("/<application_id>/status", methods=["GET", "PUT"])
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

    @application_ns.doc("get_application_status")
    @application_ns.marshal_with(application_status, code=200)
    def get(self, application_id):
        status = APPLICATIONS.get_status(application_id)
        if not status:
            abort(404)
        return status

    @application_ns.doc("put_status", parser=query_params_parser)
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
