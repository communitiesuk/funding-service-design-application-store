from db import db
from db.models import applications
from db.models.common import Status
from sqlalchemy.types import JSON
from sqlalchemy_utils import UUIDType
from sqlalchemy.orm.properties import ColumnProperty


class Sections(db.model):

        id = db.Column(
            "id",
            UUIDType(binary=False),
            primary_key=True,
            nullable=False
        )

        application_id = db.Column(
            "account_id", 
            db.ForeignKey(applications.id),
            nullable=False
        )


        json = db.Column(
            "json",
            JSON()
        )

        section_name = ColumnProperty(json["section_name"])
        
        def as_section_json(self):

            return {"status" : self.status, **self.json}
