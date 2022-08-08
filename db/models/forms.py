from db import db
from db.models.applications import Applications
from db.models.common import Status
from sqlalchemy_utils.types import UUIDType
import sqlalchemy.orm.exc
import uuid
from sqlalchemy_json import NestedMutableJson


class Forms(db.Model):

        id = db.Column(
            "id",
            UUIDType(binary=False),
            default=uuid.uuid4,
            primary_key=True,
            nullable=False,
        )

        application_id = db.Column(
            "application_id", 
            db.ForeignKey(Applications.id),
            nullable=False
        )

        json = db.Column(
            "json",
            NestedMutableJson
        )

        status = db.Column(
            "status",
            db.Enum(Status),
            default="NOT_STARTED",
            nullable=False
        )

        name = db.Column("name", db.String(), nullable=False)
        
        def as_form_json(self):

            return {"status" : self.status, "name" : self.name ,**self.json}

class FormsMethods():
    @staticmethod
    def add_new_forms(forms, application_id):
        for form in forms:
            for question in form.get("questions"):
                question.update({"status": "NOT_STARTED"})
            new_form_row = Forms(application_id=application_id, json=form, name=form["form"], status=form["status"], section=form["section"])
            db.session.add(new_form_row)
            db.session.commit()

        return {"sections" : forms} 

    @staticmethod
    def get_sections_by_app_id(application_id, as_json=True):

        sections = db.session.query(Forms).filter(Forms.application_id == application_id).all()

        if as_json:

            return [ section.as_form_json() for section in sections ]

        else:

            return sections


    @staticmethod
    def get_section(application_id, section_name):

        sections = FormsMethods.get_sections_by_app_id(application_id)

        for section in sections:

            if section["section_name"] == section_name:

                return section

                
    @staticmethod
    def update_section(application_id, section_name, new_json):

        try:

            section_sql_row = db.session.query(Forms).filter(Forms.application_id == application_id, Forms.section == section_name).one()

            section_sql_row.json = new_json

            db.session.commit()

            return new_json

        except sqlalchemy.orm.exc.NoResultFound as e:

            raise e
