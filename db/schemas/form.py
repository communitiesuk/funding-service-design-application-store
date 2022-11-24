from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from db.models.forms.enums import Status
from db.models import Forms
from marshmallow.fields import Enum


class FormsRunnerSchema(SQLAlchemySchema):
    class Meta:
        model = Forms

    status = Enum(Status)
    name = auto_field()
    questions = auto_field("json")
