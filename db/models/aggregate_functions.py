import datetime

import sqlalchemy.orm.exc
from api.routes.application.helpers import get_account
from config import Config
from db import db
from db.models.applications import Applications
from db.models.applications import ApplicationsMethods
from db.models.forms import FormsMethods
from db.models.status import Status
from external_services.models.notification import Notification


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


def update_form_statuses(application_id: str, form_name: str):
    """
    Updates the question statuses of each question if a value is present

    Args:
        application_id: The application id
    """
    stored_forms = FormsMethods.get_forms_by_app_id(
        application_id, as_json=False
    )
    application_submitted_date = db.session.get(
        Applications, application_id
    ).date_submitted
    for stored_form in stored_forms:
        if stored_form.name == form_name:
            if application_submitted_date:
                stored_form.status = "SUBMITTED"
                break
            for question_page in stored_form.json:
                if (
                    question_page["status"] == "COMPLETED"
                ):
                    stored_form.status = Status.COMPLETED
                    continue
                elif (
                    question_page["status"] == "NOT_STARTED"
                    and stored_form.status.name == "COMPLETED"
                ):
                    stored_form.status = Status.IN_PROGRESS
                    continue
                elif question_page["status"] == "IN_PROGRESS":
                    stored_form.status = Status.IN_PROGRESS
                    break
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
                    answer_or_not_specified = field.get("answer", "answer_not_specified")
                    match answer_or_not_specified:
                        case "":
                            return False
                        case []:  # noqa
                            return False
                        case "answer_not_specified":
                            return False
                        # optional questions return None when blank
                        case None:
                            return True
                        # there is an answer
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


def update_statuses(application_id, form_name):
    update_question_statuses(application_id, form_name)
    update_form_statuses(application_id, form_name)
    update_application_status(application_id)


def get_application_with_forms(app_id):
    application = ApplicationsMethods.get_application_by_id(app_id)
    forms = FormsMethods.get_forms_by_app_id(app_id)
    return {**application.as_dict(), "forms": forms}


def submit_application(application_id):
    application = ApplicationsMethods.get_application_by_id(application_id)
    application.date_submitted = datetime.datetime.now(
        datetime.timezone.utc
    ).isoformat()
    application.status = "SUBMITTED"
    db.session.commit()
    account = get_account(account_id=application.account_id)
    application_with_form_json = get_application_with_forms(application_id)

    Notification.send(
        Config.NOTIFY_TEMPLATE_SUBMIT_APPLICATION,
        account.email,
        {"application": application_with_form_json},
    )
    return application_with_form_json["id"]


def update_form(application_id, form_name, question_json):
    try:
        form_sql_row = FormsMethods.get_form(application_id, form_name)
        form_sql_row.json = question_json
        db.session.commit()
        update_statuses(application_id, form_name)
        return form_sql_row.as_json()
    except sqlalchemy.orm.exc.NoResultFound as e:
        raise e
