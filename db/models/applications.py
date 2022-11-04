import random
import string
import uuid

from api.routes.application.helpers import get_fund
from api.routes.application.helpers import get_round
from db import db
from db.models.status import Status
from flask import current_app
from sqlalchemy import DateTime
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql import func
from sqlalchemy_utils.types import UUIDType


class Applications(db.Model):
    id = db.Column(
        "id",
        UUIDType(binary=False),
        default=uuid.uuid4,
        primary_key=True,
        nullable=False,
    )
    account_id = db.Column("account_id", db.String(), nullable=False)
    fund_id = db.Column("fund_id", db.String(), nullable=False)
    round_id = db.Column("round_id", db.String(), nullable=False)
    key = db.Column("key", db.String(), nullable=False)
    language = db.Column("language", db.String(), nullable=True)
    reference = db.Column(
        "reference", db.String(), nullable=False, unique=True
    )
    project_name = db.Column(
        "project_name",
        db.String(),
        nullable=True,
    )
    started_at = db.Column("started_at", DateTime(), server_default=func.now())
    status = db.Column(
        "status", ENUM(Status), default="NOT_STARTED", nullable=False
    )
    date_submitted = db.Column("date_submitted", DateTime())
    last_edited = db.Column("last_edited", DateTime())

    __table_args__ = (
        db.UniqueConstraint("fund_id", "round_id", "key", name="_reference"),
    )

    def as_dict(self):
        date_submitted = (
            self.date_submitted.isoformat() if self.date_submitted else "null"
        )
        return {
            "id": str(self.id),
            "account_id": self.account_id,
            "round_id": self.round_id,
            "fund_id": self.fund_id,
            "language": self.language or "en",
            "reference": self.reference,
            "project_name": self.project_name or None,
            "started_at": self.started_at.isoformat(),
            "status": self.status.name,
            "last_edited": (self.last_edited or self.started_at).isoformat(),
            "date_submitted": date_submitted,
        }


class ApplicationsMethods:
    @staticmethod
    def get_application_by_id(app_id):
        application = db.session.get(Applications, app_id)
        if application is None:
            raise NoResultFound
        return application

    @staticmethod
    def get_application_status(app_id):
        application = ApplicationsMethods.get_application_by_id(app_id)
        return application.status

    @staticmethod
    def random_key_generator(length: int = 6):
        key = "".join(random.choices(string.ascii_uppercase, k=length))
        while True:
            yield key

    @staticmethod
    def _create_application_try(
        account_id, fund_id, round_id, key, language, reference, attempt
    ):
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

    @staticmethod
    def create_application(account_id, fund_id, round_id, language):
        fund = get_fund(fund_id)
        fund_round = get_round(fund_id, round_id)
        if fund and fund_round and fund.short_name and fund_round.short_name:
            new_application = None
            max_tries = 10
            attempt = 0
            key = None
            app_key_gen = ApplicationsMethods.random_key_generator()
            while attempt < max_tries and new_application is None:
                key = next(app_key_gen)
                new_application = ApplicationsMethods._create_application_try(
                    account_id=account_id,
                    fund_id=fund_id,
                    round_id=round_id,
                    key=key,
                    language=language,
                    reference="-".join(
                        [fund.short_name, fund_round.short_name, key]
                    ),
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

    @staticmethod
    def get_all():
        application_list = db.session.query(Applications).all()
        return application_list

    @staticmethod
    def search_applications(**params):
        """
        Returns a list of applications matching required params
        """
        matching_applications = []
        # datetime_start = params.get("datetime_start")
        # datetime_end = params.get("datetime_end")
        fund_id = params.get("fund_id")
        round_id = params.get("round_id")
        account_id = params.get("account_id")
        status_only = params.get("status_only")
        application_id = params.get("application_id")

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
            filters.append(Applications.status == status_only)
        if application_id:
            filters.append(Applications.id == application_id)
        if len(filters) == 0:
            matching_applications = db.session.query(Applications).all()
        else:
            matching_applications = (
                db.session.query(Applications).filter(*filters).all()
            )
        matching_applications_jsons = [
            app.as_dict() for app in matching_applications
        ]
        return matching_applications_jsons


class ApplicationTestMethods:
    @staticmethod
    def get_random_app():
        applications_list = ApplicationsMethods.get_all()
        random_app = random.choice(applications_list)
        return random_app


class ApplicationError(Exception):
    """Exception raised for errors in Application management

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message="Sorry, there was a problem, please try later"):
        self.message = message
        super().__init__(self.message)
