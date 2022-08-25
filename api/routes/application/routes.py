import uuid
from db.models.aggregate_functions import get_application_with_forms, submit_application, update_form
from db.models.applications import ApplicationsMethods
from db.models.forms import FormsMethods
from flask.views import MethodView
from flask import request
from api.routes.application.helpers import ApplicationHelpers
from sqlalchemy.orm.exc import NoResultFound

class ApplicationsView(ApplicationsMethods, MethodView):

    def get(self, **kwargs):
        print(kwargs)
        response_headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": True,
        }
        applications = ApplicationsMethods.search_applications(**kwargs)
        return applications, 200, response_headers

    def post(self):
        args = request.get_json()
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
        return application.as_dict(), 201
    
    def get_by_id(self, application_id):
        try:
            return_dict = get_application_with_forms(
                uuid.UUID(application_id)
            )
            return return_dict, 200
        except NoResultFound as e:
            return {"code": 404, "message": str(e)}

    def put(self):
        # TODO : Whatever adams wants to to with this :shrug:
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
            return {"code": 404, "message": str(e)}

    def submit(self, application_id):
        try:
            return_dict = submit_application(application_id)
            return return_dict, 201
        except KeyError as e:
            return {"code": 404, "message": str(e)}
