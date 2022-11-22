import csv
import io
import re
from datetime import datetime
from datetime import timezone

import api.routes.application.helpers
import sqlalchemy.orm.exc
from config import Config
from db import db
from db.models.applications import ApplicationsMethods
from db.models.forms import FormsMethods
from db.models.status import Status
from flask import abort
from flask import current_app
from sqlalchemy.sql import func


def update_application_status(application_id: str):
    """
    Updates the application status for an entire application,
    based on status of individual forms

    Args:
        application_id: The application id
    """
    application = ApplicationsMethods.get_application_by_id(application_id)
    forms = FormsMethods.get_forms_by_app_id(application_id, as_json=False)
    form_statuses = [form.status.name for form in forms]
    if "IN_PROGRESS" in form_statuses:
        status = "IN_PROGRESS"
    elif "COMPLETED" in form_statuses and "NOT_STARTED" in form_statuses:
        status = "IN_PROGRESS"
    elif "COMPLETED" in form_statuses:
        status = "COMPLETED"
    elif "SUBMITTED" in form_statuses:
        status = "SUBMITTED"
    else:
        status = "NOT_STARTED"
    application.status = status
    db.session.commit()


def update_form_statuses(
    application_id: str,
    form_name: str,
    is_summary_page_submitted: bool = False,
):
    """
    Updates the question statuses of each question if a value is present

    Args:
        application_id: The application id
    """
    stored_forms = FormsMethods.get_forms_by_app_id(
        application_id, as_json=False
    )
    current_form = [
        stored_form
        for stored_form in stored_forms
        if stored_form.name == form_name
    ][0]
    status_list = [question["status"] for question in current_form.json]
    if "COMPLETED" not in status_list:
        current_form.status = "NOT_STARTED"
    elif "NOT_STARTED" not in status_list and current_form.has_completed:
        current_form.status = "COMPLETED"
    elif "NOT_STARTED" not in status_list and is_summary_page_submitted:
        current_form.status = "COMPLETED"
        current_form.has_completed = True
    else:
        current_form.status = "IN_PROGRESS"
    db.session.commit()


def update_question_statuses(application_id: str, form_name: str):
    """
    Updates the question statuses of each question if a value is present

    Args:
        application_id: The application id
    """
    stored_forms = FormsMethods.get_forms_by_app_id(
        application_id, as_json=False
    )
    for stored_form in stored_forms:
        if stored_form.name == form_name:
            for question_page in stored_form.json:
                question_page["status"] = question_page.get(
                    "status", "NOT_STARTED"
                )
                if question_page["status"] == "SUBMITTED":
                    break

                def is_field_answered(field):
                    answer_or_not_specified = field.get(
                        "answer", "answer_not_specified"
                    )
                    match answer_or_not_specified:  # noqa
                        case "":
                            return False
                        case []:  # noqa (E211)
                            return False
                        case "answer_not_specified":
                            return False
                        # optional questions return None (not string)
                        # when submitted with no answer
                        case None:
                            return True
                        # default case when there is an answer
                        case _:
                            return True

                answer_found_list = [
                    is_field_answered(field)
                    for field in question_page["fields"]
                ]
                # If all answers are given
                if all(answer_found_list):
                    question_page["status"] = "COMPLETED"
                # If some answers are given
                elif not all(
                    [not found_answer for found_answer in answer_found_list]
                ):
                    question_page["status"] = "IN_PROGRESS"
                # If no answers are given
                else:
                    question_page["status"] = "NOT_STARTED"
    db.session.commit()


def update_statuses(
    application_id, form_name, is_summary_page_submitted=False
):
    update_question_statuses(application_id, form_name)
    update_form_statuses(application_id, form_name, is_summary_page_submitted)
    update_application_status(application_id)


def get_round_name(fund_id, round_id):
    response = api.routes.application.helpers.get_data(
        Config.FUND_STORE_API_HOST
        + Config.FUND_ROUND_ENDPOINT.format(fund_id=fund_id, round_id=round_id)
    )
    if response:
        return response.get("title")


def get_application_with_forms(app_id):
    application = ApplicationsMethods.get_application_by_id(app_id)
    forms = FormsMethods.get_forms_by_app_id(app_id)
    fund_id = application.as_dict().get("fund_id")
    round_id = application.as_dict().get("round_id")
    round_name = get_round_name(fund_id, round_id)
    return {**application.as_dict(), "round_name": round_name, "forms": forms}


def submit_application(application_id):
    current_app.logger.info(
        "Processing database submission for application_id:"
        f" '{application_id}."
    )
    application = ApplicationsMethods.get_application_by_id(application_id)
    application.date_submitted = datetime.now(timezone.utc).isoformat()
    application.status = "SUBMITTED"
    db.session.commit()
    return application


def update_form(
    application_id, form_name, question_json, is_summary_page_submit
):
    try:
        form_sql_row = FormsMethods.get_form(application_id, form_name)
        # Running update form for the first time
        if question_json and not form_sql_row.json:
            update_application_and_related_form(
                application_id,
                question_json,
                form_name,
                is_summary_page_submit,
            )
        # Removing all data in the form (should not be allowed)
        elif form_sql_row.json and not question_json:
            current_app.logger.error(
                "Application update aborted for application_id:"
                f" '{application_id}. Invalid data supplied"
            )
            raise Exception("ABORTING UPDATE, INVALID DATA GIVEN")
        # Updating form subsequent times
        elif form_sql_row.json and form_sql_row.json != question_json:
            update_application_and_related_form(
                application_id,
                question_json,
                form_name,
                is_summary_page_submit,
            )
    except sqlalchemy.orm.exc.NoResultFound as e:
        raise e
    db.session.commit()
    return form_sql_row.as_json()


def update_project_name(form_name, question_json, application):
    if form_name in ("project-information", "gwybodaeth-am-y-prosiect"):
        for question in question_json:
            for field in question["fields"]:
                # field id for project name in json
                if field["key"] == "KAgrBz":
                    try:
                        application.project_name = field["answer"]
                    except KeyError:
                        current_app.logger.info("Project name was not edited")
                        continue


def update_application_and_related_form(
    application_id, question_json, form_name, is_summary_page_submit
):
    application = ApplicationsMethods.get_application_by_id(application_id)
    if application.status == Status.SUBMITTED:
        current_app.logger.error(
            "Not allowed. Attempted to PUT data into a SUBMITTED application"
            f" with an application_id: {application_id}."
        )
        abort(400, "Not allowed to edit a submitted application.")

    application.last_edited = func.now()
    form_sql_row = FormsMethods.get_form(application_id, form_name)
    update_project_name(form_name, question_json, application)
    form_sql_row.json = question_json
    update_statuses(application_id, form_name, is_summary_page_submit)
    db.session.commit()
    current_app.logger.info(
        f"Application updated for application_id: '{application_id}."
    )


def export_json_to_csv(return_data, headers=None):
    output = io.StringIO()
    if type(return_data) == list:
        if not headers:
            headers = return_data[0].keys()
        w = csv.DictWriter(output, headers)
        w.writeheader()
        w.writerows(return_data)
    else:
        w = csv.DictWriter(output, return_data.keys())
        w.writeheader()
        w.writerow(return_data)
    bytes_object = bytes(output.getvalue(), encoding="utf-8")
    bytes_output = io.BytesIO(bytes_object)
    return bytes_output


def get_report_for_application(application_id):
    return get_report_for_all_applications(application_id)


def get_general_status_applications_report():
    return ApplicationsMethods.get_count_by_status()


KEY_REPORT_FIELDS = [
    "eoi_reference",
    "organisation_name",
    "organisation_type",
    "asset_type",
    "geography",
    "capital",
    "revenue",
]


def get_report_for_all_applications(
    application_id=None,
):
    """

    :param application_id: generate report for only this application ID
    (if not specified all applications are queried)
    :return: list of dict
    """
    if application_id:
        applications = [
            ApplicationsMethods.get_application_by_id(application_id)
        ]
    else:
        applications = ApplicationsMethods.get_all(status=Status.SUBMITTED)
    return_json_list = []
    for application in applications:
        return_json = {field: None for field in KEY_REPORT_FIELDS}
        stored_forms = [form.as_json() for form in application.forms]
        report_fields = [
            {
                "form_name": "organisation-information",
                "key": "WWWWxy",
                "return_field": "eoi_reference",
            },
            {
                "form_name": "organisation-information",
                "key": "YdtlQZ",
                "return_field": "organisation_name",
            },
            {
                "form_name": "organisation-information",
                "key": "lajFtB",
                "return_field": "organisation_type",
            },
            {
                "form_name": "asset-information",
                "key": "yaQoxU",
                "return_field": "asset_type",
            },
            {
                "form_name": "project-information",
                "key": "yEmHpp",
                "return_field": "geography",
            },
            {
                "form_name": "funding-required",
                "key": "JzWvhj",
                "return_field": "capital",
            },
            {
                "form_name": "funding-required",
                "key": "jLIgoi",
                "return_field": "revenue",
            },
        ]
        for form in stored_forms:
            if form.get("name") in [
                form.get("form_name") for form in report_fields
            ]:
                for question in form["questions"]:
                    for field in question["fields"]:
                        if field.get("key") in [
                            form.get("key") for form in report_fields
                        ]:
                            return_field = [
                                form.get("return_field")
                                for form in report_fields
                                if form.get("key") == field.get("key")
                            ][0]
                            if field.get("key") == "yEmHpp" and field.get(
                                "answer"
                            ):
                                postcode = re.search(
                                    "([A-Za-z][A-Ha-hJ-Yj-y]?[0-9][A-Za-z0-9]?"
                                    " ?[0-9][A-Za-z]{2}|[Gg][Ii][Rr]"
                                    " ?0[Aa]{2})",  # noqa
                                    field.get("answer"),
                                )
                                return_json[return_field] = postcode.group()
                            else:
                                return_json[return_field] = field.get("answer")
        return_json_list.append(return_json)
    return return_json_list
