import json
from dateutil import parser as date_parser

def expected_data_within_get_response(test_client, endpoint: str, expected_data):
    """Given a endpoint and expected content, check to see if response contains expected data

    Args:
        test_client: A flask test client
        endpoint (str): The GET request endpoint
        expected_data: The content we expect to find

    """

    response = test_client.get(endpoint, follow_redirects=True)
    response_data = json.loads(response.data)
    assert response_data == expected_data




def test_fund_endpoint_get(flask_test_client):
    """
    GIVEN We have a functioning Application Store API
    WHEN a GET /fund/fund-name?application_id request is sent
    THEN the response should contain the application object
    """
    expected_data = {
            "id": "uuidv4",
            "name": "Test Fund Name",
            "questions": {
                "q1": "a1"
            },
            "date_submitted": "2021-12-25 00:00:00"
        }

    expected_data_within_get_response(flask_test_client, "/fund/slugified_test_fund_name?application_id=uuidv4", expected_data)
