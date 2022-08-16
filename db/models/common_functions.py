import datetime

import sqlalchemy.orm.exc
from config import Config
from db import db
from db.models.applications import Applications
from db.models.applications import ApplicationsMethods
from db.models.forms import FormsMethods
from external_services.models.account import AccountMethods
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
    elif "COMPLETED" and "NOT_STARTED" in form_statuses:
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
    # THIS NEEDS FIXING
    forms = FormsMethods.get_forms_by_app_id(application_id, as_json=False)
    application_submitted_date = db.session.get(
        Applications, application_id
    ).date_submitted
    for form in forms:
        if form.name == form_name:
            if application_submitted_date:
                form.status = "SUBMITTED"
                break
            for question in form.json:
                if (
                    question["status"] == "COMPLETED"
                    and form.status != "IN_PROGRESS"
                ):
                    form.status = "COMPLETED"
                    continue
                elif (
                    question["status"] == "NOT_STARTED"
                    and form.status == "COMPLETED"
                ):
                    form.status = "IN_PROGRESS"
                    continue
                elif question["status"] == "IN_PROGRESS":
                    form.status = "IN_PROGRESS"
                    break
    db.session.commit()


def update_question_statuses(application_id: str, form_name: str):
    """
    Updates the question statuses of each question if a value is present

    Args:
        application_id: The application id
    """

    forms = FormsMethods.get_forms_by_app_id(application_id, as_json=False)
    for form in forms:
        if form.name == form_name:
            question_amount = len(form.json)
            for question in form.json:

                try:

                    question_status = question["status"]

                except KeyError:

                    question["status"] = "NOT_STARTED"

                    question_status = question["status"]

                if question_status == "SUBMITTED":

                    break

                if question_amount == 1:

                    question["status"] = "IN_PROGRESS"

                    break


                # field.get("answer", True) is used because if an answer
                # is optional or not given then it doesnt exist.

                def is_field_answered(field):

                    # No answer -> True (Optional pages+questions lack answer key)
                    # Answer = "" -> False
                    # Answer = None -> False

                    answer_or_not_specified = field.get("answer", False)

                    is_just_whitespace = lambda answer: answer.isspace()

                    match answer_or_not_specified:


                        case "":
                            # Means question wasnt answered
                            return False
                        case []:
                            return False
                        case None:
                            # Optional Field which hasnt been filled out.
                            return True
                        case _:
                            return True


                answer_found_list = [
                    is_field_answered(field)
                    for field in question["fields"]
                ]

                # If all answers are given
                if all(answer_found_list):
                    question["status"] = "COMPLETED"
                # If no answers are given
                elif not all(
                    [not found_answer for found_answer in answer_found_list]
                ):
                    question["status"] = "IN_PROGRESS"
                # If some answers are given
                else:
                    question["status"] = "NOT_STARTED"

    db.session.commit()


def update_statuses(application_id, form_name):

    update_question_statuses(application_id, form_name)
    update_form_statuses(application_id, form_name)
    update_application_status(application_id)


def get_application_bundle_by_id(app_id):

    application = ApplicationsMethods.get_application_by_id(app_id)

    forms = FormsMethods.get_forms_by_app_id(app_id)

    return {**application.as_dict(), "forms": forms}


def submit_application(application_id):

    application = ApplicationsMethods.get_application_by_id(application_id)

    application.date_submitted = datetime.datetime.now(
        datetime.timezone.utc
    ).strftime("%Y-%m-%d %H:%M:%S")

    db.commit()

    update_statuses(application_id)

    account = AccountMethods.get_account(
        account_id=application.get("account_id")
    )

    # Send notification
    Notification.send(
        Config.NOTIFY_TEMPLATE_SUBMIT_APPLICATION,
        account.email,
        # TODO
        {
            "application": ApplicationsMethods.get_application_bundle_by_id(
                application_id
            )
        },
    )

    return ApplicationsMethods.get_application_bundle_by_id(application_id)


def update_form(application_id, form_name, question_json):

    try:
        form_sql_row = FormsMethods.get_form(application_id, form_name)
        form_sql_row.json = question_json
        db.session.commit()

        update_statuses(application_id, form_name)

        return form_sql_row.as_json()

    except sqlalchemy.orm.exc.NoResultFound as e:

        raise e
