import pytest
from config.key_report_mappings.cof_r3w2_key_report_mapping import (
    COF_R3W2_KEY_REPORT_MAPPING,
)
from db.models import Applications
from db.models import EndOfApplicationSurveyFeedback
from db.models import Feedback
from db.models import Forms
from db.queries.feedback import retrieve_all_feedbacks_and_surveys

app_sections = [
    {"id": 62, "title": "1. About your organisation"},
    {"id": 65, "title": "2. About your project"},
]

applications = [
    Applications(
        id="app_1",
        forms=[
            Forms(
                name="applicant-information-cof-r3-w2",
                json=[
                    {
                        "questions": "Lead contact details",
                        "fields": [{"key": "NlHSBg", "answer": "test@test.com"}],
                    }
                ],
            ),
            Forms(
                name="organisation-information-cof-r3-w2",
                json=[
                    {
                        "questions": "organisation information",
                        "fields": [
                            {"key": "WWWWxy", "answer": "Ref1234"},
                            {"key": "YdtlQZ", "answer": "OrgName"},
                            {"key": "lajFtB", "answer": "Non-Profit"},
                        ],
                    }
                ],
            ),
        ],
        feedbacks=[
            Feedback(
                section_id="62",
                feedback_json={
                    "comment": "test_comment",
                    "rating": "neither easy or difficult",
                },
            ),
            Feedback(
                section_id="65",
                feedback_json={
                    "comment": "test_comment",
                    "rating": "neither easy or difficult",
                },
            ),
        ],
        end_of_application_survey=[
            EndOfApplicationSurveyFeedback(
                id=1,
                application_id="app_1",
                fund_id="test_fund",
                round_id="test_round",
                page_number=1,
                data={
                    "overall_application_experience": "neither easy or difficult",
                    "hours_spent": 45,
                },
            )
        ],
    )
]


@pytest.mark.parametrize(
    "app_sections,applications,report_mapping",
    [
        ([app_sections, applications, COF_R3W2_KEY_REPORT_MAPPING.mapping]),
    ],
)
def test_retrieve_all_feedbacks_and_surveys(mocker, app_sections, applications, report_mapping):
    mocker.patch(
        "db.queries.feedback.queries.get_application_sections",
        return_value=app_sections,
    )
    mocker.patch(
        "db.queries.feedback.queries.get_applications",
        return_value=applications,
    )
    mocker.patch(
        "db.queries.feedback.queries.get_report_mapping_for_round",
        return_value=report_mapping,
    )

    result = retrieve_all_feedbacks_and_surveys("test_fund", "test_round", "SUBMITTED")
    assert "sections_feedback" in result
    assert "end_of_application_survey_data" in result

    # check contents
    assert result["sections_feedback"][0]["section"] == app_sections[0]["title"]
    assert result["sections_feedback"][0]["comment"] == applications[0].feedbacks[0].feedback_json["comment"]
    assert result["sections_feedback"][0]["rating"] == applications[0].feedbacks[0].feedback_json["rating"]


@pytest.mark.parametrize(
    "app_sections,applications",
    [
        (
            [
                app_sections,
                applications,
            ]
        ),
    ],
)
def test_api_get_all_feedbacks_and_survey_report(
    mocker,
    flask_test_client,
    app_sections,
    applications,
):
    mocker.patch(
        "db.queries.feedback.queries.get_application_sections",
        return_value=app_sections,
    )
    mocker.patch(
        "db.queries.feedback.queries.get_applications",
        return_value=applications,
    )
    response = flask_test_client.get(
        "/applications/get_all_feedbacks_and_survey_report?fund_id=test_fund&round_id=test_round&status_only=SUBMITTED",
        headers={"Content-Type": "application/vnd.ms-excel"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert "application/vnd.ms-excel" == response.headers["Content-Type"]
    assert isinstance(response.content, bytes)
