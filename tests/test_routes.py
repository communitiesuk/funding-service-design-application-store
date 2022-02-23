def expected_data_within_get_response(test_client, endpoint: str, expected_data):
    """Given a endpoint and expected content, check to see if response contains expected data

    Args:
        test_client: A flask test client
        endpoint (str): The GET request endpoint
        expected_data: The content we expect to find

    """

    response = test_client.get(endpoint, follow_redirects=True)
    assert str(expected_data) in str(response.data)


def test_fund_endpoint_get(flask_test_client):
    """
    GIVEN We have a functioning Application Store API
    WHEN a /fund GET request is sent
    THEN the response should contain the test fund name
    """
    expected_data = "test-fund"
    expected_data_within_get_response(flask_test_client, "/fund", expected_data)




