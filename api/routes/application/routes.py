import uuid

from api.routes.application.helpers import ApplicationHelpers
from api.routes.application.helpers import get_account
from config import Config
from db.models.aggregate_functions import export_json_to_csv
from db.models.aggregate_functions import get_application_with_forms
from db.models.aggregate_functions import (
    get_general_status_applications_report,
)
from db.models.aggregate_functions import get_report_for_all_applications
from db.models.aggregate_functions import get_report_for_application
from db.models.aggregate_functions import KEY_REPORT_FIELDS
from db.models.aggregate_functions import submit_application
from db.models.aggregate_functions import update_form
from db.models.applications import ApplicationsMethods
from db.models.forms import FormsMethods
from external_services.exceptions import NotificationError
from external_services.models.notification import Notification
from flask import current_app
from flask import request
from flask import send_file
from flask.views import MethodView
from sqlalchemy.orm.exc import NoResultFound


class ApplicationsView(ApplicationsMethods, MethodView):
    def get(self, **kwargs):
        response_headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": True,
        }
        matching_applications = ApplicationsMethods.search_applications(
            **kwargs
        )
        order_by = kwargs.get("order_by", None)
        order_rev = kwargs.get("order_rev", None)
        sorted_applications = ApplicationHelpers.order_applications(
            matching_applications, order_by, order_rev
        )
        return sorted_applications, 200, response_headers

    def post(self):
        args = request.get_json()
        account_id = args["account_id"]
        round_id = args["round_id"]
        fund_id = args["fund_id"]
        language = args["language"]
        empty_forms = ApplicationHelpers.get_blank_forms(
            fund_id, round_id, language
        )
        application = ApplicationsMethods.create_application(
            account_id=account_id,
            fund_id=fund_id,
            round_id=round_id,
            language=language,
        )
        FormsMethods.add_new_forms(
            forms=empty_forms, application_id=application.id
        )
        return application.as_dict(), 201

    def get_by_id(self, application_id):
        try:
            return_dict = get_application_with_forms(uuid.UUID(application_id))
            return return_dict, 200
        except ValueError as e:
            current_app.logger.error(
                "Value error getting application ID: {application_id}"
            )
            raise e
        except NoResultFound as e:
            return {"code": 404, "message": str(e)}

    def get_key_application_data_report(self, application_id):
        try:
            return send_file(
                export_json_to_csv(get_report_for_application(application_id)),
                "text/csv",
                as_attachment=True,
                download_name="required_data.csv",
            )
        except NoResultFound as e:
            return {"code": 404, "message": str(e)}

    def get_applications_statuses_report(self):
        try:
            return send_file(
                export_json_to_csv(get_general_status_applications_report()),
                "text/csv",
                as_attachment=True,
                download_name="required_data.csv",
            )
        except NoResultFound as e:
            return {"code": 404, "message": str(e)}

    def get_key_applications_data_report(self):
        try:
            return send_file(
                export_json_to_csv(
                    get_report_for_all_applications(), KEY_REPORT_FIELDS
                ),
                "text/csv",
                as_attachment=True,
                download_name="required_data.csv",
            )
        except NoResultFound as e:
            return {"code": 404, "message": str(e)}

    def put(self):
        request_json = request.get_json(force=True)
        form_dict = {
            "application_id": request_json["metadata"]["application_id"],
            "form_name": request_json["metadata"].get("form_name"),
            "question_json": request_json["questions"],
            "is_summary_page_submit": request_json["metadata"].get(
                "isSummaryPageSubmit", False
            ),
        }
        try:
            updated_form = update_form(**form_dict)
            return updated_form, 201
        except NoResultFound as e:
            return {"code": 404, "message": str(e)}

    def submit(self, application_id):
        try:
            application = submit_application(application_id)
            account = get_account(account_id=application.account_id)
            application_with_form_json = get_application_with_forms(
                application_id
            )

            Notification.send(
                Config.NOTIFY_TEMPLATE_SUBMIT_APPLICATION,
                account.email,
                {"application": application_with_form_json},
            )
            return {
                "id": application_id,
                "reference": application_with_form_json["reference"],
                "email": account.email,
            }, 201
        except KeyError as e:
            return {"code": 404, "message": str(e)}
        except NotificationError as e:
            current_app.logger.exception(
                "Notification error on sending SUBMIT notification for"
                f" application {application_id}"
            )
            return str(e), 500, {"x-error": "notification error"}
        except Exception as e:
            current_app.logger.exception(
                "Error on sending SUBMIT notification for application"
                f" {application_id}"
            )
            return str(e), 500, {"x-error": "Error"}
