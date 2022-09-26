import uuid

from db import db
from db.models.applications import Applications
from db.models.status import Status
from sqlalchemy_json import NestedMutableJson
from sqlalchemy_utils.types import UUIDType


class Forms(db.Model):
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
    status = db.Column(
        "status", db.Enum(Status), default="NOT_STARTED", nullable=False
    )
    name = db.Column("name", db.String(), nullable=False)
    has_completed = db.Column("has_completed", db.Boolean(), default=False)

    def as_json(self):
        return {
            "status": self.status.name,
            "name": self.name,
            "questions": self.json,
        }


class FormsMethods:
    @staticmethod
    def add_new_forms(forms, application_id):
        for form in forms:
            new_form_row = Forms(
                application_id=application_id,
                json=form["questions"],
                name=form["form_minting_name"],
                status="NOT_STARTED",
            )
            db.session.add(new_form_row)
            db.session.commit()
        return {"forms": forms}

    @staticmethod
    def get_forms_by_app_id(application_id, as_json=True):
        forms = (
            db.session.query(Forms)
            .filter(Forms.application_id == application_id)
            .all()
        )
        if as_json:
            return [form.as_json() for form in forms]
        else:
            return forms

    @staticmethod
    def get_form(application_id, form_name):
        return (
            db.session.query(Forms)
            .filter(
                Forms.application_id == application_id, Forms.name == form_name
            )
            .one()
        )
