from db import db
from db.models.forms.forms import Forms
from db.queries import get_feedback
from db.queries.application import get_application
from db.queries.feedback import retrieve_end_of_application_survey_data
from db.queries.form.queries import get_form
from external_services import get_round
from external_services.data import get_application_sections


def update_application_status(application_id: str):
    """
    Updates the application status for an entire application,
    based on status of individual forms

    Args:
        application_id: The application id
    """
    application = get_application(application_id)

    all_feedback_completed = True
    round_instance = get_round(application.fund_id, application.round_id)
    if round_instance and round_instance.requires_feedback:
        sections = get_application_sections(
            application.fund_id, application.round_id, application.language.name
        )
        sections_feedbacks_completed = all(
            get_feedback(application_id, str(s["id"]))
            for s in sections
            if s.get("requires_feedback")
        )
        end_of_feedback_survey_completed = all(
            retrieve_end_of_application_survey_data(application_id, pn) for pn in "1234"
        )
        all_feedback_completed = (
            sections_feedbacks_completed and end_of_feedback_survey_completed
        )

    form_statuses = [form.status.name for form in application.forms]
    if "IN_PROGRESS" in form_statuses:
        status = "IN_PROGRESS"
    elif (
        "COMPLETED" in form_statuses
        and "NOT_STARTED" in form_statuses
        or not all_feedback_completed
    ):
        status = "IN_PROGRESS"
    elif "COMPLETED" in form_statuses and all_feedback_completed:
        status = "COMPLETED"
    elif "SUBMITTED" in form_statuses:
        status = "SUBMITTED"
    else:
        status = "NOT_STARTED"
    application.status = status


def update_form_status(
    form_to_update: Forms,
    is_summary_page_submitted: bool = False,
):
    """
    Updates the status of a whole form based on the statuses of all questions within the form

    Parameters:
        form_to_update (`Forms'): Forms object that we want to update.
        This object is updated by this function so needs to be within the DB context
        is_summary_page_submit (`bool`): Whether or not this is an update from submitting the summary page

    """

    status_list = [question["status"] for question in form_to_update.json]
    if "COMPLETED" not in status_list:
        form_to_update.status = "NOT_STARTED"
    elif "NOT_STARTED" not in status_list and form_to_update.has_completed:
        form_to_update.status = "COMPLETED"
    elif "NOT_STARTED" not in status_list and is_summary_page_submitted:
        form_to_update.status = "COMPLETED"
        form_to_update.has_completed = True
    else:
        form_to_update.status = "IN_PROGRESS"


def _is_field_answered(field: dict) -> bool:
    """
    Determines whether or not an answer has been provided for the supplied field.

    Parameters:
    field (`dict`): The field we want to find and answer for

    Returns:
    bool: Whether or not the field has been answered
    """
    answer_or_not_specified = field.get("answer")
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


def _determine_answer_status_for_fields(fields_in_question: list[dict]) -> list[bool]:
    """
    Builds a list of bools representing which fields have been answered in the supplied question

    Parameters:
    fields_in_question (`list[dict]`): The fields element from a question in the form

    Returns:
    list: True or False for each field in the question, eg. `[True, True, False]`
    """
    answer_found_list = [_is_field_answered(field) for field in fields_in_question]
    return answer_found_list


def _determine_question_status_from_answers(answer_found_list: list[bool]) -> str:
    """
    Determines the status of this question, based on the supplied list of whether each field is answered

    Parameters:
        answer_found_list (`list[bool]`): Whether or not each field in the question has an answer,
        eg. `[True, True, False]`

    Returns:
        str: The status of this question
    """

    # If we found no answers
    if not answer_found_list:
        return "NOT_STARTED"
    # If all answers are given
    if all(answer_found_list):
        return "COMPLETED"
    # If some answers are given
    elif any(answer_found_list):
        return "IN_PROGRESS"
    # If no answers are given
    else:
        return "NOT_STARTED"


def update_question_statuses(stored_form_json: dict):
    """
    Updates `status` field in every question in this form object, based on whether or not answers are supplied

    Parameters:
        stored_form_json: The json object, within the db context, representing the form to update.
        This same object will be updated by this function.

    """
    for question_page in stored_form_json:
        question_page["status"] = question_page.get("status", "NOT_STARTED")

        # doesn't look like we ever set a question_page status to be SUBMITTED
        # if question_page["status"] == "SUBMITTED":
        #     break

        answer_found_list = _determine_answer_status_for_fields(question_page["fields"])
        question_page["status"] = _determine_question_status_from_answers(
            answer_found_list
        )


def update_statuses(application_id, form_name, is_summary_page_submitted=False):
    form_to_update = get_form(application_id=application_id, form_name=form_name)
    update_question_statuses(stored_form_json=form_to_update.json)
    update_form_status(form_to_update, is_summary_page_submitted)
    db.session.commit()
    update_application_status(application_id)
    db.session.commit()
