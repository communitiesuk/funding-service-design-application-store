import datetime
from db import db
from sqlalchemy import DateTime
from db.models.common import Status
from sqlalchemy_utils.types import UUIDType

import enum

def started_at():

    raw_date = datetime.datetime.now(datetime.timezone.utc)
    formatted_date = raw_date.strftime("%Y-%m-%d %H:%M:%S")
    return formatted_date

class Applications(db.model):

        id = db.Column(
            "id",
            UUIDType(binary=False),
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

        started_at = db.Column("created_at", DateTime(), default=datetime.utcnow)
        
        status = db.Column(
            "status",
            db.Enum(Status),
            default="NOT_STARTED",
            nullable=False
        )

        date_submitted = db.Column("date_submitted", DateTime())

        last_edited = db.Column("last_edited", DateTime())
        
        def as_json(self):

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
