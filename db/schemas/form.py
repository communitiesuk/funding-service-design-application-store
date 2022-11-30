from db.models import Forms
from db.models.forms.enums import Status
from marshmallow.fields import Enum
from marshmallow_sqlalchemy import auto_field
from marshmallow_sqlalchemy import SQLAlchemySchema


class FormsRunnerSchema(SQLAlchemySchema):
    class Meta:
        model = Forms

    status = Enum(Status)
    name = auto_field()
    questions = auto_field("json")
