import datetime
from db.models.applications import Applications, ApplicationsMethods
from db import db
from db.models.forms import FormsMethods
from external_services.models.account import AccountMethods
from external_services.models.notification import Notification
from config import Config

def update_application_status(application_id: str):
    """
    Updates the application status for an entire application,
    based on status of individual sections

    Args:
        application_id: The application id
    """
    application = ApplicationsMethods.get_application_by_id(application_id)
    sections = FormsMethods.get_sections_by_app_id(application_id, as_json=False)
    section_statuses = [section.json["status"] for section in sections]
    if "IN_PROGRESS" in section_statuses:
        status = "IN_PROGRESS"
    elif "COMPLETED" and "NOT_STARTED" in section_statuses:
        status = "IN_PROGRESS"
    elif "COMPLETED" in section_statuses:
        status = "COMPLETED"
    elif "SUBMITTED" in section_statuses:
        status = "SUBMITTED"
    else:
        status = "NOT_STARTED"
    application.status = status
    db.session.commit()

def update_section_statuses(application_id: str):
    """
    Updates the question statuses of each question if a value is present

    Args:
        application_id: The application id
    """
    sections = FormsMethods.get_sections_by_app_id(application_id, as_json=False)
    application_submitted_date = db.session.get(Applications, application_id).date_submitted
    for section in sections:
        section["status"] = section.get("status", "NOT_STARTED")
        if application_submitted_date:
                section["status"] = "SUBMITTED"
                break
        for question in section["questions"]:
            if (
                question["status"] == "COMPLETED"
                and section["status"] != "IN_PROGRESS"
            ):
                section["status"] = "COMPLETED"
                continue
            elif (
                question["status"] == "NOT_STARTED"
                and section["status"] == "COMPLETED"
            ):
                section["status"] = "IN_PROGRESS"
                continue
            elif question["status"] == "IN_PROGRESS":
                section["status"] = "IN_PROGRESS"
                break
    db.session.commit()

def update_question_statuses(application_id: str):
    """
    Updates the question statuses of each question if a value is present

    Args:
        application_id: The application id
    """

    sections = FormsMethods.get_sections_by_app_id(application_id, as_json=False)
    application_submitted_date = db.session.get(Applications, application_id).date_submitted
    for section in sections:
        for question in section.json["questions"]:
            question["status"] = "NOT_STARTED"
            if application_submitted_date:
                    question["status"] = "SUBMITTED"
                    break
            for index, field in enumerate(question["fields"]):
                field_answered = (
                    True
                    if "answer" in field
                    and field["answer"] != ""
                    and field["answer"] is not None
                    else False
                )
                first_field_in_question = True if index == 0 else False
                all_fields_complete = (
                    True if question["status"] == "COMPLETED" else False
                )
                question_complete_or_partially_complete = (
                    True
                    if question["status"] == ("COMPLETED" or "IN_PROGRESS")
                    else False
                )
                if field_answered and (
                    all_fields_complete or first_field_in_question
                ):
                    question["status"] = "COMPLETED"
                elif field_answered:
                    question["status"] = "IN_PROGRESS"
                elif not question_complete_or_partially_complete:
                    question["status"] = "NOT_STARTED"

    db.session.commit()

def update_statuses(application_id):

    update_question_statuses(application_id)
    update_section_statuses(application_id)
    update_application_status(application_id)

def get_application_bundle_by_id(app_id):

    application = ApplicationsMethods.get_application_by_id(app_id)

    forms = FormsMethods.get_sections_by_app_id(app_id)

    return {**application.as_dict(), "forms" : forms}

def submit_application(application_id):

    application = ApplicationsMethods.get_application_by_id(application_id)

    application.date_submitted = datetime.datetime.now(
        datetime.timezone.utc
    ).strftime("%Y-%m-%d %H:%M:%S")

    db.commit()

    update_statuses(application_id)

    account = AccountMethods.get_account(account_id=application.get("account_id"))

    # Send notification
    Notification.send(
        Config.NOTIFY_TEMPLATE_SUBMIT_APPLICATION,
        account.email,
        # TODO 
        {"application": ApplicationsMethods.get_application_bundle_by_id(application_id)},
    )

    return ApplicationsMethods.get_application_bundle_by_id(application_id)