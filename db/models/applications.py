from datetime import datetime
from db import db
from sqlalchemy import DateTime
from db.models.common import Status
from sqlalchemy_utils.types import UUIDType
import uuid

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
            nullable=False
        )

        account_id = db.Column(
            "account_id", 
            db.String(),
            nullable=False
        )

        round_id = db.Column(
            "round_id", 
            db.String(),
            nullable=False
        )
        
        fund_id = db.Column(
            "fund_id", 
            db.String(),
            nullable=False
        )

        project_name = db.Column(
            "project_name", 
            db.String(),
        )

        started_at = db.Column("created_at", DateTime(), default=datetime.today())
        
        status = db.Column(
            "status",
            db.Enum(Status),
            default="NOT_STARTED",
            nullable=False
        )

        date_submitted = db.Column("date_submitted", DateTime())

        last_edited = db.Column("last_edited", DateTime())
        
        def as_dict(self):

            return {
                "id" : str(self.id),
                "account_id" : self.account_id,
                "round_id" : self.round_id,
                "fund_id" : self.fund_id,
                "project_name" : self.project_name,
                "started_at" : self.started_at.strftime("%Y-%m-%d %H:%M:%S"),
                "status" : self.status,
                "date_submitted" : self.date_submitted,
                "last_edited" : self.last_edited
            }
        

class ApplicationsMethods():
    @staticmethod
    def create_application(account_id,fund_id,round_id):

        new_application_row = Applications(account_id=account_id, fund_id=fund_id, round_id=round_id)

        db.session.add(new_application_row)

        db.session.commit()
        
        return new_application_row

    @staticmethod
    def search_applications(filters: dict, as_dict: bool):
        if filters:
            filter_list = []
            # if the filter dictionary key has a value, add this filter to the db search parameters
            for filter, value in filters.items():
                if value:
                    filter_list.append(getattr(Applications, filter).contains(value))
            applications = Applications.query.filter(*filter_list).all()
        else:
            applications = Applications.query.all()
        if as_dict:
            return [application.as_dict() for application in applications]
        return applications
