from marshmallow.fields import DateTime, Enum
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field

from db.models import Feedback
from db.models.feedback.enums import Status


class FeedbackSchema(SQLAlchemySchema):
    class Meta:
        model = Feedback

    application_id = auto_field()
    fund_id = auto_field()
    round_id = auto_field()
    status = Enum(Status)
    section_id = auto_field()
    feedback_json = auto_field()
    date_submitted = DateTime(format="iso")
