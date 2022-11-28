import uuid

from db import db
from db.models.application.applications import Applications
from .enums import Status
from sqlalchemy_json import NestedMutableJson
from sqlalchemy_utils.types import UUIDType
from flask_sqlalchemy import DefaultMeta

BaseModel: DefaultMeta = db.Model

class Forms(BaseModel):
    __table_args__ = (db.UniqueConstraint("id", "name"),)
    id = db.Column(
        "id",
        UUIDType(binary=False),
        default=uuid.uuid4,
        primary_key=True,
        nullable=False,
    )
    application_id = db.Column(
        "application_id", db.ForeignKey(Applications.id), nullable=False
    )
    json = db.Column("json", NestedMutableJson)
    status = db.Column("status", db.Enum(Status), default="NOT_STARTED", nullable=False)
    name = db.Column("name", db.String(), nullable=False)
    has_completed = db.Column("has_completed", db.Boolean(), default=False)

    def as_json(self):
        return {
            "status": self.status.name,
            "name": self.name,
            "questions": self.json,
        }

