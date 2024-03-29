import sqlalchemy
from db import db
from db.models.application.enums import Status as ApplicationStatus
from db.queries.application import attempt_to_find_and_update_project_name
from db.queries.application import get_application
from db.queries.form import get_form
from db.queries.statuses import update_statuses
from flask import abort
from flask import current_app
from sqlalchemy import func


def update_application_and_related_form(application_id, question_json, form_name, is_summary_page_submit):
    application = get_application(application_id)
    if application.status == ApplicationStatus.SUBMITTED:
        current_app.logger.error(
            f"Not allowed. Attempted to PUT data into a SUBMITTED application with an application_id: {application_id}."
        )
        abort(400, "Not allowed to edit a submitted application.")

    application.last_edited = func.now()
    form_sql_row = get_form(application_id, form_name)
    if (project_name := attempt_to_find_and_update_project_name(question_json, application)) is not None:
        application.project_name = project_name
    form_sql_row.json = question_json
    update_statuses(application_id, form_name, is_summary_page_submit)
    db.session.commit()
    current_app.logger.info(f"Application updated for application_id: '{application_id}.")


def update_form(application_id, form_name, question_json, is_summary_page_submit):
    try:
        form_sql_row = get_form(application_id, form_name)
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
                f"Application update aborted for application_id: '{application_id}. Invalid data supplied"
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
