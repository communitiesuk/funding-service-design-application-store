import random
import uuid

from db import db
from db.models.status import Status
from sqlalchemy import DateTime
from sqlalchemy.dialects.postgresql import ENUM
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
    round_id = db.Column("round_id", db.String(), nullable=False)
    fund_id = db.Column("fund_id", db.String(), nullable=False)
    project_name = db.Column(
        "project_name",
        db.String(),
    )
    started_at = db.Column("started_at", DateTime(), server_default=func.now())
    status = db.Column(
        "status", ENUM(Status), default="NOT_STARTED", nullable=False
    )
    date_submitted = db.Column("date_submitted", DateTime())
    last_edited = db.Column("last_edited", DateTime())

    def as_dict(self):
        date_submitted = (
            self.date_submitted.isoformat() if self.date_submitted else "null"
        )
        return {
            "id": str(self.id),
            "account_id": self.account_id,
            "round_id": self.round_id,
            "fund_id": self.fund_id,
            "project_name": self.project_name
            or "Project details not filled in",
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
    def create_application(account_id, fund_id, round_id):
        new_application_row = Applications(
            account_id=account_id, fund_id=fund_id, round_id=round_id
        )
        db.session.add(new_application_row)
        db.session.commit()
        return new_application_row

    @staticmethod
    def get_all():
        application_list = db.session.query(Applications).all()
        return application_list

    @staticmethod
    def application_edited(app_id):
        application = ApplicationsMethods.get_application_by_id(app_id)
        application.last_edited = func.now()
        db.session.commit()

    def search_applications(**params):
        """
        Returns a list of applications matching required params
        """
        matching_applications = []
        # datetime_start = params.get("datetime_start")
        # datetime_end = params.get("datetime_end")
        fund_id = params.get("fund_id")
        account_id = params.get("account_id")
        status_only = params.get("status_only")
        application_id = params.get("application_id")

        filters = []
        if fund_id:
            filters.append(Applications.fund_id == fund_id)
        if account_id:
            filters.append(Applications.account_id == account_id)
        if status_only:
            filters.append(
                Applications.status.name == status_only.replace(" ", "_")
            )
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
