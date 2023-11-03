from db.models import EndOfApplicationSurveyFeedback
from marshmallow_sqlalchemy import auto_field
from marshmallow_sqlalchemy import SQLAlchemySchema


class EndOfApplicationSurveyFeedbackSchema(SQLAlchemySchema):
    class Meta:
        model = EndOfApplicationSurveyFeedback

    application_id = auto_field()
    fund_id = auto_field()
    round_id = auto_field()
    data = auto_field()
    page_number = auto_field()
