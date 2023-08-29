from datetime import datetime

from db import db
from db.models import Feedback
from db.models.feedback import EndOfApplicationSurveyFeedback


def upsert_feedback(
    application_id, fund_id, round_id, section_id, feedback_json, status
):
    existing_feedback = Feedback.query.filter_by(
        application_id=application_id,
        fund_id=fund_id,
        round_id=round_id,
        section_id=section_id,
    ).first()

    if existing_feedback:
        existing_feedback.feedback_json = feedback_json
        existing_feedback.status = status
        existing_feedback.date_submitted = datetime.now()
        db.session.commit()
        return existing_feedback
    else:
        new_feedback_row = Feedback(
            application_id=application_id,
            fund_id=fund_id,
            round_id=round_id,
            section_id=section_id,
            feedback_json=feedback_json,
            status=status,
            date_submitted=datetime.now(),
        )
        db.session.add(new_feedback_row)
        db.session.commit()
        return new_feedback_row


def get_feedback(application_id, section_id):
    return (
        db.session.query(Feedback)
        .filter(
            Feedback.application_id == application_id, Feedback.section_id == section_id
        )
        .one()
    )


def upsert_end_of_application_survey_data(
    application_id, fund_id, round_id, page_number, data
):
    existing_survey_data = EndOfApplicationSurveyFeedback.query.filter_by(
        application_id=application_id,
        fund_id=fund_id,
        round_id=round_id,
        page_number=page_number,
    ).first()

    if existing_survey_data:
        existing_survey_data.data = data
        existing_survey_data.date_submitted = datetime.now()
        db.session.commit()
        return existing_survey_data
    else:
        new_survey_data = EndOfApplicationSurveyFeedback(
            application_id=application_id,
            fund_id=fund_id,
            round_id=round_id,
            page_number=page_number,
            data=data,
            date_submitted=datetime.now(),
        )
        db.session.add(new_survey_data)
        db.session.commit()
        return new_survey_data


def retrieve_end_of_application_survey_data(application_id, page_number):
    return (
        db.session.query(EndOfApplicationSurveyFeedback)
        .filter(
            EndOfApplicationSurveyFeedback.application_id == application_id,
            EndOfApplicationSurveyFeedback.page_number == page_number,
        )
        .one()
    )
