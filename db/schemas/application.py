from db.models import Applications
from db.models.application.enums import Language
from db.models.application.enums import Status
from external_services import get_round_name
from marshmallow import post_dump
from marshmallow.fields import DateTime
from marshmallow.fields import Enum
from marshmallow.fields import Method
from marshmallow_sqlalchemy import auto_field
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow_sqlalchemy.fields import Nested

from .form import FormsRunnerSchema


class ApplicationSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Applications
        exclude = ["key"]

    @post_dump
    def handle_nones(self, data, **kwargs):
        if data["last_edited"] is None:
            data["last_edited"] = data["started_at"]
        if data["date_submitted"] is None:
            data["date_submitted"] = "null"
        if data["language"] is None:
            data["language"] = "en"
        return data

    def get_round_name(self, obj):
        return get_round_name(obj.fund_id, obj.round_id)

    language = Enum(Language, default=Language.en)
    project_name = auto_field()
    started_at = DateTime(format="iso")
    status = Enum(Status)
    last_edited = DateTime(format="iso")
    round_name = Method("get_round_name")
    forms = Nested(FormsRunnerSchema, many=True, allow_none=True)
