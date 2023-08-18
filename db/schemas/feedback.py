from db.models import Feedback
from db.models.feedback.enums import Status
from marshmallow.fields import Enum
from marshmallow_sqlalchemy import auto_field
from marshmallow_sqlalchemy import SQLAlchemySchema
from marshmallow.fields import DateTime

class FeedbackSchema(SQLAlchemySchema):
    class Meta:
        model = Feedback

    id = auto_field()
    application_id = auto_field()
    fund_id = auto_field()
    round_id = auto_field()
    status = Enum(Status)
    section_id = auto_field()
    feedback_json = auto_field()
    date_submitted = DateTime(format="iso")