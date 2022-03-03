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


def test_application_post_and_application_get(flask_test_client):
    """
    GIVEN We have a functioning Application Store API
    WHEN a number of new application are posted
    THEN the api stores these applications within the correct fund
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
