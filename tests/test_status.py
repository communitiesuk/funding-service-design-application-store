from tests.helpers import expected_data_within_get_response
from tests.helpers import put_response_return_200


def test_update_status_response(flask_test_client):
    """
    Summary:
        Confirm that a PUT on /application/<application_id>/status
        with question_name and new_status as query args
        correctly updates status of the given question
    Args:
        flask_test_client
    """
    # Test get response with GET request for NOT STARTED & COMPLETED
    expected_data_NOT_STARTED = {
        "id": "uuidv4",
        "status": "COMPLETED",
        "fund_id": "test-fund-name",
        "round_id": "spring",
        "date_submitted": "2021-12-24 00:00:00",
        "assessment_deadline": "2022-08-28 00:00:00",
        "questions": [
            {
                "question": "Q1",
                "status": "NOT STARTED",
            },
            {
                "question": "Q2",
                "status": "COMPLETED",
            },
        ]
    }
    expected_data_within_get_response(
        flask_test_client,
        "/application/uuidv4/status",
        expected_data_NOT_STARTED,
    )

    # Test get response with PUT & GET request for IN PROGRESS & COMPLETED
    expected_data_IN_PROGRESS = {
        "id": "uuidv4",
        "status": "COMPLETED",
        "fund_id": "test-fund-name",
        "round_id": "spring",
        "date_submitted": "2021-12-24 00:00:00",
        "assessment_deadline": "2022-08-28 00:00:00",
        "questions": [
            {
                "question": "Q1",
                "status": "IN PROGRESS",
            },
            {
                "question": "Q2",
                "status": "COMPLETED",
            },
        ]
    }
    put_response_return_200(
        flask_test_client,
        "/application/uuidv4/status" + "?new_status=IN PROGRESS&question_name=Q1",
    )
    expected_data_within_get_response(
        flask_test_client,
        "/application/uuidv4/status",
        expected_data_IN_PROGRESS,
    )

    # Test get response with get request for COMPLETED & COMPLETED
    expected_data_COMPLETED = {
        "id": "uuidv4",
        "status": "COMPLETED",
        "fund_id": "test-fund-name",
        "round_id": "spring",
        "date_submitted": "2021-12-24 00:00:00",
        "assessment_deadline": "2022-08-28 00:00:00",
        "questions": [
            {
                "question": "Q1",
                "status": "COMPLETED",
            },
            {
                "question": "Q2",
                "status": "COMPLETED",
            },
        ]
    }
    put_response_return_200(
        flask_test_client,
        "/application/uuidv4/status" + "?new_status=COMPLETED&question_name=Q1",
    )
    expected_data_within_get_response(
        flask_test_client,
        "/application/uuidv4/status",
        expected_data_COMPLETED,
    )
