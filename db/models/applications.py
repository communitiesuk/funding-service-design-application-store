import datetime
import random
import uuid
from operator import itemgetter

from db import db
from db.models.status import Status
from sqlalchemy import DateTime
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql import func
from sqlalchemy_utils.types import UUIDType


def started_at():
    raw_date = datetime.datetime.now(datetime.timezone.utc)
    formatted_date = raw_date.strftime("%Y-%m-%d %H:%M:%S")
    return formatted_date


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
        return {
            "id": str(self.id),
            "account_id": self.account_id,
            "round_id": self.round_id,
            "fund_id": self.fund_id,
            "project_name": self.project_name,
            "started_at": self.started_at.strftime("%Y-%m-%d %H:%M:%S"),
            "status": self.status.name,
            "date_submitted": self.date_submitted,
            "last_edited": self.last_edited,
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

    def search_applications(params):
        """
        Returns a list of applications matching required params
        """
        matching_applications = []
        # datetime_start = params.get("datetime_start")
        # datetime_end = params.get("datetime_end")
        fund_id = params.get("fund_id")
        account_id = params.get("account_id")
        status_only = params.get("status_only")
        id_contains = params.get("id_contains")
        order_by = params.get("order_by", "id")
        order_rev = params.get("order_rev") == "1"
        filters = []
        if fund_id:
            filters.append(Applications.fund_id == fund_id)
        if account_id:
            filters.append(Applications.account_id == account_id)
        if status_only:
            filters.append(
                Applications.status.name == status_only.replace(" ", "_")
            )
        if id_contains:
            filters.append(Applications.id.contains(id_contains))
        if len(filters) == 0:
            matching_applications = db.session.query(Applications).all()
        else:
            matching_applications = (
                db.session.query(Applications).filter(*filters).all()
            )
        matching_applications_jsons = [
            app.as_dict() for app in matching_applications
        ]
        if order_by and order_by in [
            "id",
            "status",
            "account_id",
            "assessment_deadline",
        ]:
            sorted_matching_applications_jsons = sorted(
                matching_applications_jsons,
                key=itemgetter(order_by),
                reverse=order_rev,
            )
        else:
            sorted_matching_applications_jsons = matching_applications_jsons
        return sorted_matching_applications_jsons


class ApplicationTestMethods:
    @staticmethod
    def get_random_app():
        applications_list = ApplicationsMethods.get_all()
        random_app = random.choice(applications_list)
        return random_app
