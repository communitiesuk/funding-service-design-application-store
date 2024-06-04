from copy import deepcopy
from datetime import datetime

from db import db
from db.models.research import ResearchSurvey


def upsert_research_survey_data(application_id, fund_id, round_id, data) -> ResearchSurvey:
    existing_survey_data = ResearchSurvey.query.filter_by(
        application_id=application_id,
        fund_id=fund_id,
        round_id=round_id,
    ).first()

    if existing_survey_data:
        existing_form_data = deepcopy(existing_survey_data.data)
        existing_form_data.update(data)
        existing_survey_data.data = existing_form_data
        existing_survey_data.date_submitted = datetime.now()
        db.session.commit()
        return existing_survey_data

    new_survey_data = ResearchSurvey(
        application_id=application_id,
        fund_id=fund_id,
        round_id=round_id,
        data=data,
        date_submitted=datetime.now(),
    )
    db.session.add(new_survey_data)
    db.session.commit()
    return new_survey_data


def retrieve_research_survey_data(application_id) -> ResearchSurvey:
    return (
        db.session.query(ResearchSurvey)
        .filter(
            ResearchSurvey.application_id == application_id,
        )
        .one_or_none()
    )
