from unittest.mock import MagicMock

import pytest
from db.queries.statuses.queries import _determine_question_status_from_answers
from db.queries.statuses.queries import _is_field_answered
from db.queries.statuses.queries import update_form_status
from db.queries.statuses.queries import update_question_statuses


@pytest.mark.parametrize(
    "answer_found_list,exp_status",
    [
        ([True], "COMPLETED"),
        ([True, True], "COMPLETED"),
        ([False, False], "NOT_STARTED"),
        ([False], "NOT_STARTED"),
        ([True, False], "IN_PROGRESS"),
        ([True, False, True], "IN_PROGRESS"),
        ([], "NOT_STARTED"),
        (None, "NOT_STARTED"),
    ],
)
def test_determine_question_status_from_answers(answer_found_list, exp_status):
    assert _determine_question_status_from_answers(answer_found_list) == exp_status


@pytest.mark.parametrize(
    "field_json,exp_result",
    [
        ({"answer": "abc"}, True),
        ({"answer": 123}, True),
        ({"answer": None}, True),
        ({"answer": ["abc", 123]}, True),
        ({"answer": ""}, False),
        ({"answer": []}, False),
    ],
)
def test_is_field_answered(field_json, exp_result):
    assert _is_field_answered(field_json) == exp_result


def test_update_question_statuses_with_mocks(mocker):
    mock_question_status = mocker.patch(
        "db.queries.statuses.queries._determine_question_status_from_answers",
        return_value="NOT_STARTED",
    )
    mock_answer_status = mocker.patch(
        "db.queries.statuses.queries._determine_answer_status_for_fields"
    )

    test_json = [{"fields": [], "status": None}, {"fields": [], "status": None}]

    update_question_statuses(test_json)

    assert test_json[0]["status"] == "NOT_STARTED"
    assert test_json[1]["status"] == "NOT_STARTED"
    mock_question_status.call_count == 2
    mock_answer_status.call_count == 2


@pytest.mark.parametrize(
    "form_json,exp_status",
    [
        ([{"fields": [{"answer": "hello"}], "status": None}], "COMPLETED"),
        (
            [
                {"fields": [{"answer": "hello"}, {"answer": ""}], "status": None},
                {"fields": [{"answer": "hello"}, {"answer": ""}], "status": None},
            ],
            "IN_PROGRESS",
        ),
        ([{"fields": [{"answer": ""}], "status": None}], "NOT_STARTED"),
    ],
)
def test_update_question_statuses(form_json, exp_status):
    update_question_statuses(form_json)
    for form in form_json:
        assert form["status"] == exp_status


@pytest.mark.parametrize(
    "form_json,form_has_completed,is_summary_submit,exp_status,exp_has_completed",
    [
        ([{"status": "NOT_STARTED"}], False, False, "NOT_STARTED", False),
        (
            [{"status": "IN_PROGRESS"}, {"status": "COMPLETED"}],
            False,
            False,
            "IN_PROGRESS",
            False,
        ),
        (
            [{"status": "NOT_STARTED"}, {"status": "COMPLETED"}],
            False,
            False,
            "IN_PROGRESS",
            False,
        ),
        (
            [{"status": "COMPLETED"}, {"status": "COMPLETED"}],
            False,
            False,
            "IN_PROGRESS",
            False,
        ),
        (
            [{"status": "COMPLETED"}, {"status": "COMPLETED"}],
            False,
            True,
            "COMPLETED",
            True,
        ),
        ([{"status": "NOT_STARTED"}], True, False, "NOT_STARTED", True),
        ([{"status": "COMPLETED"}], True, False, "COMPLETED", True),
    ],
)
def test_update_form_status(
    form_json, form_has_completed, is_summary_submit, exp_status, exp_has_completed
):
    form_to_update = MagicMock()
    form_to_update.json = form_json
    form_to_update.has_completed = form_has_completed
    update_form_status(form_to_update, is_summary_submit)
    assert form_to_update.status == exp_status
    assert form_to_update.has_completed == exp_has_completed
