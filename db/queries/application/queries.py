import random
import string
from datetime import datetime
from datetime import timezone
from itertools import groupby
from typing import Dict
from typing import List
from typing import Optional

from db import db
from db.exceptions import ApplicationError
from db.models import Applications
from db.models.application.enums import Status as ApplicationStatus
from db.schemas import ApplicationSchema
from external_services import get_fund
from external_services import get_round
from external_services.aws import FileData
from external_services.aws import list_files_by_prefix
from flask import current_app
from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import noload
from sqlalchemy.sql.expression import Select


def get_application(app_id, include_forms=False, as_json=False) -> Dict | Applications:

    stmt: Select = select(Applications).filter(Applications.id == app_id)

    if include_forms:
        stmt.options(joinedload(Applications.forms))
        serialiser = ApplicationSchema()
    else:
        stmt.options(noload(Applications.forms))
        serialiser = ApplicationSchema(exclude=["forms"])

    row: Applications = db.session.scalars(stmt).unique().one()

    if as_json:
        json_row = serialiser.dump(row)
        return json_row
    else:
        return row


def get_applications(
    filters=[], include_forms=False, as_json=False
) -> List[Dict] | List[Applications]:

    stmt: Select = select(Applications)

    if len(filters) > 0:
        stmt = stmt.where(*filters)

    if include_forms:
        stmt = stmt.options(joinedload(Applications.forms))
        serialiser = ApplicationSchema()
    else:
        stmt = stmt.options(noload(Applications.forms))
        serialiser = ApplicationSchema(exclude=["forms"])

    rows: Applications = db.session.scalars(stmt).unique().all()

    if as_json:
        return [serialiser.dump(row) for row in rows]
    else:
        return rows


def get_application_status(app_id):
    application = get_application(app_id)
    return application.status


def random_key_generator(length: int = 6):
    key = "".join(random.choices(string.ascii_uppercase, k=length))
    while True:
        yield key


def _create_application_try(
    account_id, fund_id, round_id, key, language, reference, attempt
) -> Applications:
    try:
        new_application_row = Applications(
            account_id=account_id,
            fund_id=fund_id,
            round_id=round_id,
            key=key,
            language=language,
            reference=reference,
        )
        db.session.add(new_application_row)
        db.session.commit()
        return new_application_row
    except IntegrityError:
        db.session.remove()
        current_app.logger.error(
            f"Failed {attempt} attempt(s) to create application with"
            f" application reference {reference}, for fund_id"
            f" {fund_id} and round_id {round_id}"
        )


def create_application(account_id, fund_id, round_id, language) -> Applications:
    fund = get_fund(fund_id)
    fund_round = get_round(fund_id, round_id)
    application_start_language = language
    if language == "cy" and not fund.welsh_available:
        application_start_language = "en"
    if fund and fund_round and fund.short_name and fund_round.short_name:
        new_application = None
        max_tries = 10
        attempt = 0
        key = None
        app_key_gen = random_key_generator()
        while attempt < max_tries and new_application is None:
            key = next(app_key_gen)
            new_application = _create_application_try(
                account_id=account_id,
                fund_id=fund_id,
                round_id=round_id,
                key=key,
                language=application_start_language,
                reference="-".join([fund.short_name, fund_round.short_name, key]),
                attempt=attempt,
            )
            attempt += 1

        if not new_application:
            raise ApplicationError(
                f"Max ({max_tries}) tries exceeded for create application"
                f" with application key {key}, for fund.short_name"
                f" {fund.short_name} and round.short_name"
                f" {fund_round.short_name}"
            )
        return new_application
    else:
        raise ApplicationError(
            f"Failed to create application. Fund round {round_id} for fund"
            f" {fund_id} not found"
        )


def get_all_applications() -> List:
    application_list = db.session.query(Applications).all()
    return application_list


def get_count_by_status(
    round_id: Optional[str] = None, fund_id: Optional[str] = None
) -> Dict[str, int]:
    query = db.session.query(Applications.status, func.count(Applications.status))

    if round_id is not None:
        query = query.filter_by(round_id=round_id)
    if fund_id is not None:
        query = query.filter_by(fund_id=fund_id)

    status_query = query.group_by(Applications.status).all()
    statuses_with_counts = {status[0].name: status[1] for status in status_query}

    return {**{s.name: 0 for s in ApplicationStatus}, **statuses_with_counts}


def search_applications(**params):
    """
    Returns a list of applications matching required params
    """
    # datetime_start = params.get("datetime_start")
    # datetime_end = params.get("datetime_end")
    fund_id = params.get("fund_id")
    round_id = params.get("round_id")
    account_id = params.get("account_id")
    status_only = params.get("status_only")
    application_id = params.get("application_id")
    forms = params.get("forms")

    filters = []
    if fund_id:
        filters.append(Applications.fund_id == fund_id)
    if round_id:
        filters.append(Applications.round_id == round_id)
    if account_id:
        filters.append(Applications.account_id == account_id)
    if status_only:
        if " " in status_only:
            status_only = status_only.replace(" ", "_")
        if type(status_only) == list:
            filters.append(Applications.status.in_(status_only))
        else:
            filters.append(Applications.status == status_only)
    if application_id:
        filters.append(Applications.id == application_id)
    found_apps = get_applications(filters, include_forms=forms, as_json=True)
    return found_apps


def submit_application(application_id) -> Applications:
    current_app.logger.info(
        f"Processing database submission for application_id: '{application_id}."
    )
    application = get_application(application_id)
    application.date_submitted = datetime.now(timezone.utc).isoformat()

    all_application_files = list_files_by_prefix(application_id)
    application = process_files(application, all_application_files)

    application.status = "SUBMITTED"
    db.session.commit()
    return application


def process_files(application: Applications, all_files: list[FileData]) -> Applications:
    comp_id_to_files = {
        comp_id: list(files)
        for comp_id, files in groupby(all_files, key=lambda x: x.component_id)
    }
    for form in application.forms:
        for component in form.json:
            for field in component["fields"]:
                comp_id = field["key"]
                if files := comp_id_to_files.get(comp_id):
                    field["answer"] = ", ".join(state.filename for state in files)
    return application


def update_project_name(form_name, question_json, application) -> None:
    if form_name.startswith("project-information") or form_name.startswith(
        "gwybodaeth-am-y-prosiect"
    ):
        for question in question_json:
            for field in question["fields"]:
                # field id for project name in json
                if field["title"] == "Project name":
                    try:
                        application.project_name = field["answer"]
                    except KeyError:
                        current_app.logger.info("Project name was not edited")
                        continue


def get_fund_id(application_id):
    """Function takes an application_id and returns the fund_id of that application."""
    try:
        application = (
            db.session.query(Applications).filter_by(id=application_id).first()
        )
        if application:
            return application.fund_id
        else:
            return None
    except Exception:
        current_app.logger.error(f"Incorrect application id: {application_id}")
        return None


def attempt_to_find_and_update_project_name(question_json, application) -> None:
    """
    Updates the applications project name if the updated question_json
    contains a field_id match on the pre-configured project_name field_id.
    """
    round = get_round(application.fund_id, application.round_id)
    project_name_field_id = round.project_name_field_id

    for question in question_json:
        for field in question["fields"]:
            if field["key"] == project_name_field_id:
                return field["answer"]
