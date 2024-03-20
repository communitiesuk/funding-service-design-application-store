import time
from typing import Optional
from uuid import uuid4

from _helpers import get_blank_forms
from _helpers import order_applications
from config import Config
from config.key_report_mappings.mappings import ROUND_ID_TO_KEY_REPORT_MAPPING
from db.models.application.enums import Status
from db.queries import add_new_forms
from db.queries import create_application
from db.queries import export_json_to_csv
from db.queries import export_json_to_excel
from db.queries import get_application
from db.queries import get_feedback
from db.queries import get_fund_id
from db.queries import get_general_status_applications_report
from db.queries import get_key_report_field_headers
from db.queries import get_report_for_applications
from db.queries import search_applications
from db.queries import submit_application
from db.queries import update_form
from db.queries import upsert_feedback
from db.queries.feedback import retrieve_all_feedbacks_and_surveys
from db.queries.feedback import retrieve_end_of_application_survey_data
from db.queries.feedback import upsert_end_of_application_survey_data
from db.queries.reporting.queries import export_application_statuses_to_csv
from db.queries.reporting.queries import map_application_key_fields
from db.queries.statuses import update_statuses
from external_services import get_account
from external_services import get_fund
from external_services import get_round
from external_services import get_round_eoi_schema
from external_services.aws import _SQS_CLIENT
from external_services.exceptions import NotificationError
from external_services.models.notification import Notification
from flask import current_app
from flask import request
from flask import send_file
from flask.views import MethodView
from fsd_utils import Eoi_Decision
from fsd_utils import evaluate_eoi_response
from fsd_utils.config.notify_constants import NotifyConstants
from sqlalchemy.orm.exc import NoResultFound


class ApplicationsView(MethodView):
    def get(self, **kwargs):
        response_headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": True,
        }
        matching_applications = search_applications(**kwargs)
        order_by = kwargs.get("order_by", None)
        order_rev = kwargs.get("order_rev", None)
        sorted_applications = order_applications(matching_applications, order_by, order_rev)
        return sorted_applications, 200, response_headers

    def post(self):
        args = request.get_json()
        account_id = args["account_id"]
        round_id = args["round_id"]
        fund_id = args["fund_id"]
        language = args["language"]
        fund = get_fund(fund_id=fund_id)
        if language == "cy" and not fund.welsh_available:
            language = "en"
        empty_forms = get_blank_forms(fund_id=fund_id, round_id=round_id, language=language)
        application = create_application(
            account_id=account_id,
            fund_id=fund_id,
            round_id=round_id,
            language=language,
        )
        add_new_forms(forms=empty_forms, application_id=application.id)
        return application.as_dict(), 201

    def get_by_id(self, application_id):
        try:
            return_dict = get_application(application_id, as_json=True, include_forms=True)
            return return_dict, 200
        except ValueError as e:
            current_app.logger.error("Value error getting application ID: {application_id}")
            raise e
        except NoResultFound as e:
            return {"code": 404, "message": str(e)}, 404

    def get_key_application_data_report(self, application_id):
        try:
            return send_file(
                export_json_to_csv(get_report_for_applications(application_ids=[application_id])),
                "text/csv",
                as_attachment=True,
                download_name="required_data.csv",
            )
        except NoResultFound as e:
            return {"code": 404, "message": str(e)}, 404

    def get_applications_statuses_report(
        self,
        round_id: Optional[list] = [],
        fund_id: Optional[list] = [],
        format: Optional[str] = "csv",
    ):
        try:
            report_data = get_general_status_applications_report(
                round_id or None,
                fund_id or None,
            )
        except NoResultFound as e:
            return {"code": 404, "message": str(e)}, 404

        if format.lower() == "json":
            return {"metrics": report_data}
        else:
            return send_file(
                export_application_statuses_to_csv(report_data),
                "text/csv",
                as_attachment=True,
                download_name="required_data.csv",
            )

    def get_key_applications_data_report(
        self,
        status=Status.SUBMITTED.name,
        round_id: Optional[str] = None,
        fund_id: Optional[str] = None,
    ):
        try:
            return send_file(
                export_json_to_csv(
                    get_report_for_applications(status=status, round_id=round_id, fund_id=fund_id),
                    get_key_report_field_headers(round_id),
                ),
                "text/csv",
                as_attachment=True,
                download_name="required_data.csv",
            )
        except NoResultFound as e:
            return {"code": 404, "message": str(e)}, 404

    def put(self):
        request_json = request.get_json(force=True)
        form_dict = {
            "application_id": request_json["metadata"]["application_id"],
            "form_name": request_json["metadata"].get("form_name"),
            "question_json": request_json["questions"],
            "is_summary_page_submit": request_json["metadata"].get("isSummaryPageSubmit", False),
        }
        try:
            updated_form = update_form(**form_dict)
            return updated_form, 201
        except NoResultFound as e:
            return {"code": 404, "message": str(e)}, 404

    def submit(self, application_id):
        should_send_email = True
        if request.args.get("dont_send_email") == "true":
            should_send_email = False

        try:
            fund_id = get_fund_id(application_id)
            fund_data = get_fund(fund_id)
            application = submit_application(application_id)
            account = get_account(account_id=application.account_id)
            round_data = get_round(fund_id, application.round_id)
            application_with_form_json = get_application(application_id, as_json=True, include_forms=True)
            language = application_with_form_json["language"]
            fund_name = fund_data.name_json[language]
            round_name = round_data.title_json[language]
            application_with_form_json_and_fund_name = {
                **application_with_form_json,
                "fund_name": fund_name,
                "round_name": round_name,
            }
            application_attributes = {
                "application_id": {"StringValue": application_id, "DataType": "String"},
            }

            # Submit message to queue, in a future state this can trigger the
            # assessment service to import the application
            #  (currently assessment is using a CRON timer to pick up messages,
            # not a webhook for triggers)

            _SQS_CLIENT.submit_single_message(
                queue_url=Config.AWS_SQS_IMPORT_APP_PRIMARY_QUEUE_URL,
                message=application_with_form_json,
                extra_attributes=application_attributes,
                message_group_id="import_applications_group",
                message_deduplication_id=str(uuid4()),  # ensures message uniqueness
            )

            if fund_data.short_name in ("COF-EOI",):  # check if it's an EOI fund
                full_name = (
                    account.full_name
                    if account.full_name
                    else map_application_key_fields(
                        application_with_form_json,
                        ROUND_ID_TO_KEY_REPORT_MAPPING[application.round_id],
                        application.round_id,
                    ).get("lead_contact_name", "")
                )
                eoi_results = self.get_application_eoi_response(application_with_form_json)
                eoi_decision = eoi_results["decision"]
                contents = {
                    NotifyConstants.APPLICATION_FIELD: application_with_form_json_and_fund_name,
                    NotifyConstants.MAGIC_LINK_CONTACT_HELP_EMAIL_FIELD: round_data.contact_email,
                    NotifyConstants.APPLICATION_CAVEATS: eoi_results["caveats"],
                }
                if Eoi_Decision(eoi_decision) == Eoi_Decision.PASS:  # EOI Full pass
                    notify_template = Config.NOTIFY_TEMPLATE_EOI_PASS

                elif Eoi_Decision(eoi_decision) == Eoi_Decision.PASS_WITH_CAVEATS:  # EOI Pass with caveats
                    notify_template = Config.NOTIFY_TEMPLATE_EOI_PASS_W_CAVEATS
                else:
                    notify_template = None
                    should_send_email = False
            else:
                notify_template = Config.NOTIFY_TEMPLATE_SUBMIT_APPLICATION
                eoi_decision = None
                full_name = account.full_name
                contents = {
                    NotifyConstants.APPLICATION_FIELD: application_with_form_json_and_fund_name,
                    NotifyConstants.MAGIC_LINK_CONTACT_HELP_EMAIL_FIELD: round_data.contact_email,
                }

            if should_send_email:
                Notification.send(
                    notify_template,
                    account.email,
                    full_name.title() if full_name else None,
                    contents,
                )
            return {
                "id": application_id,
                "reference": application_with_form_json["reference"],
                "email": account.email,
                "eoi_decision": eoi_decision,
            }, 201
        except KeyError as e:
            current_app.logger.exception(
                f"Key error on processing application submissionfor application: '{application_id}'"
            )
            return str(e), 500, {"x-error": "key error"}
        except NotificationError as e:
            current_app.logger.exception(
                f"Notification error on sending SUBMIT notification for application {application_id}"
            )
            return str(e), 500, {"x-error": "notification error"}
        except Exception as e:
            current_app.logger.exception(f"Error on sending SUBMIT notification for application {application_id}")
            return str(e), 500, {"x-error": "Error"}

    def post_feedback(self):
        args = request.get_json()
        application_id = args["application_id"]
        fund_id = args["fund_id"]
        round_id = args["round_id"]
        section_id = args["section_id"]
        feedback_json = args["feedback_json"]
        status = args["status"]

        feedback = upsert_feedback(
            application_id=application_id,
            fund_id=fund_id,
            round_id=round_id,
            section_id=section_id,
            feedback_json=feedback_json,
            status=status,
        )

        update_statuses(application_id, form_name=None)

        return feedback.as_dict(), 201

    def get_feedback_for_section(self, application_id, section_id):
        feedback = get_feedback(application_id, section_id)
        if feedback:
            return feedback.as_dict(), 200

        return {
            "code": 404,
            "message": f"Feedback not fund for {application_id}, {section_id}",
        }, 404

    def post_end_of_application_survey_data(self):
        args = request.get_json()
        application_id = args["application_id"]
        fund_id = args["fund_id"]
        round_id = args["round_id"]
        page_number = args["page_number"]
        data = args["data"]

        survey_data = upsert_end_of_application_survey_data(
            application_id=application_id,
            fund_id=fund_id,
            round_id=round_id,
            page_number=page_number,
            data=data,
        )

        update_statuses(application_id, form_name=None)

        return survey_data.as_dict(), 201

    def get_end_of_application_survey_data(self, application_id, page_number):
        survey_data = retrieve_end_of_application_survey_data(application_id, int(page_number))
        if survey_data:
            return survey_data.as_dict(), 200

        return {
            "code": 404,
            "message": f"Survey data for {application_id}, {page_number} not found",
        }, 404

    def get_all_feedbacks_and_survey_report(self, **params):
        fund_id = params.get("fund_id")
        round_id = params.get("round_id")
        status = params.get("status_only")

        try:
            return send_file(
                path_or_file=export_json_to_excel(retrieve_all_feedbacks_and_surveys(fund_id, round_id, status)),
                mimetype="application/vnd.ms-excel",
                as_attachment=True,
                download_name=f"fsd_feedback_{str(int(time.time()))}.xlsx",
            )
        except NoResultFound as e:
            return {"code": 404, "message": str(e)}, 404

    def get_application_eoi_response(self, application):
        eoi_schema = get_round_eoi_schema(application["fund_id"], application["round_id"], application["language"])
        result = evaluate_eoi_response(eoi_schema, application["forms"])
        return result
