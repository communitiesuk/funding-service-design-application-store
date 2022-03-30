from tests.helpers import count_fund_applications
from tests.helpers import expected_data_within_get_response
from tests.helpers import post_data


def test_fund_endpoint_get_by_application_id(flask_test_client):
    """
    GIVEN We have a functioning Application Store API
    WHEN a GET /fund/fund-name?application_id request is sent
    THEN the response should contain the application object
    """

    expected_data = {
        "id": "uuidv4",
        "name": "Test Fund Name",
        "status": "NOT_STARTED",
        "assessment_deadline": "2022-08-28 00:00:00",
        "questions": [
            {
                "question": "Q1",
                "fields": [
                    {
                        "key": "applicant_name",
                        "title": "Applicant name",
                        "type": "text",
                        "answer": "Applicant",
                    }
                ],
            }
        ],
        "date_submitted": "2021-12-24 00:00:00",
    }

    application_data = {
        "name": "Test Fund Name",
        "questions": {"question": "A1"},
    }
    post_data(flask_test_client, "/fund/new_application", application_data)

    i = 0
    while i < 200:
        post_data(flask_test_client, "/fund/new_application", application_data)
        i += 1

    expected_data_within_get_response(
        flask_test_client,
        "/fund/slugified_test_fund_name?application_id=uuidv4",
        expected_data,
    )


def test_fund_endpoint_get_applications_by_time_period(flask_test_client):
    """
    GIVEN We have a functioning Application Store API
    WHEN a request for fund applications within a given time period
    THEN the response should only contain the applications that
    fall within the time period
    """
    expected_data = [
        {
            "id": "uuidv4-2",
            "name": "Test Fund Name",
            "status": "NOT_STARTED",
            "assessment_deadline": "2022-08-28 00:00:00",
            "questions": [
                {
                    "question": "Q1",
                    "fields": [
                        {
                            "key": "applicant_name",
                            "title": "Applicant name",
                            "type": "text",
                            "answer": "Applicant",
                        }
                    ],
                }
            ],
            "date_submitted": "2022-12-25 00:00:00",
        }
    ]

    expected_data_within_get_response(
        flask_test_client,
        "/fund/slugified_test_fund_name"
        "?datetime_start=2022-01-01&datetime_end=2022-12-28",
        expected_data,
    )


def test_fund_endpoint_post_application_is_successful(flask_test_client):
    """
    GIVEN We have a functioning Application Store API
    WHEN a number of new application are posted
    THEN the application stores these applications within the correct fund
    """

    expected_length_fund_a_before = 1
    expected_length_fund_a_after = 2
    expected_length_fund_b = 1

    application_data_1 = {"name": "fund-a", "questions": {"question": "A1"}}

    application_data_2 = {"name": "fund-b", "questions": {"question": "A2"}}

    application_data_3 = {"name": "fund-a", "questions": {"question": "A3"}}

    post_data(flask_test_client, "/fund/new_application", application_data_1)
    count_fund_applications(
        flask_test_client, "fund-a", expected_length_fund_a_before
    )
    post_data(flask_test_client, "/fund/new_application", application_data_2)
    count_fund_applications(
        flask_test_client, "fund-a", expected_length_fund_a_before
    )
    post_data(flask_test_client, "/fund/new_application", application_data_3)
    count_fund_applications(
        flask_test_client, "fund-a", expected_length_fund_a_after
    )
    count_fund_applications(
        flask_test_client, "fund-b", expected_length_fund_b
    )


def test_search_endpoint_get_applications_by_status(flask_test_client):
    """
    GIVEN We have a functioning Application Store API
    WHEN a request for fund applications within a given time period
    THEN the response should only contain the applications that
    fall within the time period
    """
    expected_data = [
        {
            "id": "uuidv4",
            "status": "NOT_STARTED",
            "assessment_deadline": "2022-08-28 00:00:00",
            "fund_id": "slugified_test_fund_name"
        },
        {
            "id": "uuidv4-2",
            "status": "NOT_STARTED",
            "assessment_deadline": "2022-08-28 00:00:00",
            "fund_id": "slugified_test_fund_name"
        }
    ]

    expected_data_within_get_response(
        flask_test_client,
        "/search/"
        "?status_only=not%20started",
        expected_data,
    )
