import datetime

import sqlalchemy.orm.exc
from db import db
from db.models.applications import Applications
from db.models.applications import ApplicationsMethods
from db.models.forms import FormsMethods
from db.models.status import Status
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
                if question_page["status"] == "COMPLETED":
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


def update_statuses(application_id, form_name):
    update_question_statuses(application_id, form_name)
    update_form_statuses(application_id, form_name)
    update_application_status(application_id)


def get_application_with_forms(app_id):
    application = ApplicationsMethods.get_application_by_id(app_id)
    forms = FormsMethods.get_forms_by_app_id(app_id)
    return {**application.as_dict(), "forms": forms}


def submit_application(application_id):
    current_app.logger.info(
        "Processing database submission for application_id:"
        f" '{application_id}."
    )
    application = ApplicationsMethods.get_application_by_id(application_id)
    application.date_submitted = datetime.datetime.now(
        datetime.timezone.utc
    ).isoformat()
    application.status = "SUBMITTED"
    db.session.commit()
    return application


def update_form(application_id, form_name, question_json):
    try:
        form_sql_row = FormsMethods.get_form(application_id, form_name)
        # Running update form for the first time
        if question_json and not form_sql_row.json:
            update_application_and_related_form(
                application_id, question_json, form_name
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
                application_id, question_json, form_name
            )
    except sqlalchemy.orm.exc.NoResultFound as e:
        raise e
    db.session.commit()
    return form_sql_row.as_json()


def update_application_and_related_form(
    application_id, question_json, form_name
):
    application = ApplicationsMethods.get_application_by_id(application_id)
    application.last_edited = func.now()
    form_sql_row = FormsMethods.get_form(application_id, form_name)

    if form_name == "project-information":
        current_app.logger.error(question_json)
        if len(question_json) == 3:
            fields_array = question_json[1]["fields"]
        else:
            fields_array = question_json[2]["fields"]
        for key in fields_array:
            if (key["key"] == "KAgrBz") or (key["title"] == "Project name"):
                try:
                    application.project_name = key["answer"]
                except KeyError:
                    current_app.logger.error("Project name was not edited")
                    continue

    form_sql_row.json = question_json
    update_statuses(application_id, form_name)
    db.session.commit()
    current_app.logger.info(
        f"Application updated for application_id: '{application_id}."
    )
