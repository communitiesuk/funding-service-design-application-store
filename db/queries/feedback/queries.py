from datetime import datetime

from config.key_report_mappings.mappings import get_report_mapping_for_round
from db import db
from db.models import Applications
from db.models import Feedback
from db.models.feedback import EndOfApplicationSurveyFeedback
from db.queries.application.queries import get_applications
from db.queries.reporting.queries import map_application_key_fields
from db.schemas.application import ApplicationSchema
from db.schemas.end_of_application_survey import EndOfApplicationSurveyFeedbackSchema
from external_services.data import get_application_sections
from flask import current_app


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
        .one_or_none()
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
        .one_or_none()
    )


def retrieve_all_feedbacks_and_surveys(fund_id, round_id, status):
    filters = []
    section_names = {}
    sections_feedback = []
    end_of_application_survey_data = []

    # get applications
    if fund_id:
        filters.append(Applications.fund_id == fund_id)
    if round_id:
        filters.append(Applications.round_id == round_id)
    if status:
        filters.append(Applications.status == status)
    applications = get_applications(filters=filters, include_forms=True)

    mapping_report = get_report_mapping_for_round(round_id)

    # get section id & names map
    application_sections = get_application_sections(fund_id, round_id, language="en")
    for section in application_sections:
        section_names[str(section["id"])] = section["title"]

    # extract section feedbacks & end of survey feedbacks for all applications
    eoas_serialiser = EndOfApplicationSurveyFeedbackSchema()
    applicant_serialiser = ApplicationSchema()

    for application in applications:
        # extract applicant email & organisation
        try:
            result = map_application_key_fields(
                applicant_serialiser.dump(application),
                mapping_report.mapping,
                mapping_report.round_id,
            )
            applicant_email = result["applicant_email"]
            applicant_organisation = result["organisation_name"]
        except Exception as e:
            current_app.logger.error(
                f"Coudn't extract applicant email & organisation.  Exception :{e}"
            )
            applicant_email = ""
            applicant_organisation = ""

        # extract sections feedback
        for feedback in application.feedbacks:
            sections_feedback.append(
                {
                    "application_id": str(application.id),
                    "applicant_email": applicant_email,
                    "applicant_organisation": applicant_organisation,
                    "section": section_names[feedback.section_id],
                    "comment": feedback.feedback_json["comment"],
                    "rating": feedback.feedback_json["rating"],
                }
            )

        # extract end of survey feedback
        eoas_list = [
            eoas_serialiser.dump(row) for row in application.end_of_application_survey
        ]
        total_feedback = {
            "application_id": str(application.id),
            "applicant_email": applicant_email,
            "applicant_organisation": applicant_organisation,
        }
        for eoas in eoas_list:
            for key, value in eoas["data"].items():
                if key != "csrf_token":
                    total_feedback[key] = value

        end_of_application_survey_data.append(total_feedback)

    return {
        "sections_feedback": sections_feedback,
        "end_of_application_survey_data": end_of_application_survey_data,
    }
