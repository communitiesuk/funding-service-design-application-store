import pytest
from db.models import Applications
from db.models import EndOfApplicationSurveyFeedback
from db.models import Feedback
from db.models import Forms
from db.queries.feedback import retrieve_all_feedbacks_and_surveys


@pytest.mark.parametrize(
    "app_sections,applications",
    [
        (
            [
                [
                    {"id": 62, "title": "1. About your organisation"},
                    {"id": 65, "title": "2. About your project"},
                ],
                [
                    Applications(
                        id="app_1",
                        forms=[Forms()],
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
                                    "overall_application_experience": (
                                        "neither easy or difficult"
                                    ),
                                    "hours_spent": 45,
                                },
                            )
                        ],
                    )
                ],
            ]
        ),
    ],
)
def test_retrieve_all_feedbacks_and_surveys(
    mocker,
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

    result = retrieve_all_feedbacks_and_surveys("test_fund", "test_round", "SUBMITTED")
    assert "sections_feedback" in result
    assert "end_of_application_survey_data" in result
