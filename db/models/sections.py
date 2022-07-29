from db import db
from db.models import applications
from db.models.common import Status
from sqlalchemy_utils import UUIDType


class sections(db.model):

        id = db.Column(
            "id",
            UUIDType(binary=False),
            primary_key=True,
            nullable=False
        )

        application_id = db.Column(
            "account_id", 
            db.ForeignKey(applications.id)
            nullable=False
        )
        
        status = db.Column(
            "status",
            db.Enum(Status),
            default="NOT_STARTED",
            nullable=False
        )
