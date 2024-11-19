from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field

from db.models import EndOfApplicationSurveyFeedback


class EndOfApplicationSurveyFeedbackSchema(SQLAlchemySchema):
    class Meta:
        model = EndOfApplicationSurveyFeedback

    application_id = auto_field()
    fund_id = auto_field()
    round_id = auto_field()
    data = auto_field()
    page_number = auto_field()
