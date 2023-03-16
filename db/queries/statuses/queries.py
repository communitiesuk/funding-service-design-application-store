from db import db
from db.queries.application import get_application


def update_application_status(application_id: str):
    """
    Updates the application status for an entire application,
    based on status of individual forms

    Args:
        application_id: The application id
    """
    application = get_application(application_id)

    form_statuses = [form.status.name for form in application.forms]
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
    stored_forms = get_application(
        application_id, as_json=False, include_forms=True
    ).forms

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
    stored_forms = get_application(
        application_id, as_json=False, include_forms=True
    ).forms

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
                        "answer"
                    )
                    match answer_or_not_specified:  # noqa
                        case "":
                            return False
                        case []:  # noqa (E211)
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
