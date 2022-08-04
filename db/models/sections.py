from db import db
from db.models.applications import Applications
from db.models.common import Status
from sqlalchemy.types import JSON
from sqlalchemy_utils.types import UUIDType
import uuid
from sqlalchemy.orm.properties import ColumnProperty


class Sections(db.Model):

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
            JSON()
        )

        section_name = ColumnProperty(json["section_name"])
        status = ColumnProperty(json["status"])
        
        def as_section_json(self):

            return {"status" : self.status, **self.json}

class SectionsMethods():
    @staticmethod
    def add_new_sections(sections, application_id, status="NOT_STARTED"):
        for section in sections:
            for question in section.get("questions"):
                question.update({"status": "NOT_STARTED"})
        
            new_section_row = Sections(application_id=application_id, json=section)
            db.session.add(new_section_row)
            db.session.commit()

        return {"sections" : sections} 

    @staticmethod
    def get_sections_by_app_id(application_id, as_json=True):

        sections = db.session.query(Sections).filter(Sections.application_id == application_id).all()

        if as_json:

            return [ section.json for section in sections ]

        else:

            return sections


    @staticmethod
    def get_section(application_id, section_name):

        sections = SectionsMethods.get_sections_by_app_id(application_id)

        for section in sections:

            if section["section_name"] == section_name:

                return section

                
    @staticmethod
    def update_section(self, application_id, section_name, new_json):

            section_sql_row = db.session.query(Sections).filter(Sections.application_id == application_id, Sections.section_name == section_name).one()

            section_sql_row.json = new_json

            db.session.commit()

