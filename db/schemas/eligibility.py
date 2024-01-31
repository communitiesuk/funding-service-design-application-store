from db.models import Eligibility
from db.models.eligibility.eligibility_trail import EligibilityUpdate
from marshmallow import post_dump
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema


class EligibilitySchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Eligibility
        exclude = ["key"]

    @post_dump
    def handle_nones(self, data, **kwargs):
        if data["date_submitted"] is None:
            data["date_submitted"] = "null"


class EligibilityUpdateSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = EligibilityUpdate
