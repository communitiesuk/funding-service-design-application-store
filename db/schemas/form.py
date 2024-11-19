from marshmallow.fields import Enum
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field

from db.models import Forms
from db.models.forms.enums import Status


class FormsRunnerSchema(SQLAlchemySchema):
    class Meta:
        model = Forms

    status = Enum(Status)
    name = auto_field()
    questions = auto_field("json")
