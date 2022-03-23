import json


def expected_data_within_get_response(
    test_client, endpoint: str, expected_data, debug: bool = False
):
    """
    Given a endpoint and expected content,
    check to see if response contains expected data

    Args:
        test_client: A flask test client
        endpoint (str): The GET request endpoint
        expected_data: The content we expect to find

    """

    response = test_client.get(endpoint, follow_redirects=True)
    response_data = json.loads(response.data)
    if debug:
        print("RESPONSE DATA:", response_data)
        print("Expected DATA:", expected_data)
    assert response_data == expected_data


def expected_data_within_put_response(
    test_client, endpoint: str, expected_data, debug: bool = False
):
    """
    Given a endpoint and expected content,
    check to see if response contains expected data

    Args:
        test_client: A flask test client
        endpoint (str): The PUT request endpoint
        expected_data: The content we expect to find

    """

    response = test_client.put(endpoint, follow_redirects=True)
    response_data = json.loads(response.data)
    if debug:
        print("RESPONSE DATA:", response_data)
        print("Expected DATA:", expected_data)
    assert response_data == expected_data


def post_data(flask_test_client, endpoint: str, post_data: dict):
    """Given an endpoint and data, check to see if response contains expected data

    Args:
        test_client: A flask test client
        endpoint (str): The POST request endpoint
        post_data (dict): The content to post to the endpoint provided
    """

    flask_test_client.post(
        endpoint, data=json.dumps(post_data), content_type="application/json"
    )


def put_data(flask_test_client, endpoint: str, post_data: dict):
    """Given an endpoint and data, check to see if response contains expected data

    Args:
        test_client: A flask test client
        endpoint (str): The POST request endpoint
        post_data (dict): The content to post to the endpoint provided
    """

    flask_test_client.put(
        endpoint, data=json.dumps(post_data), content_type="application/json"
    )


def count_fund_applications(
    test_client, fund_name: str, expected_application_count
):
    """
    Given a fund_name, check the number of applications stored within

    Args:
        test_client: A flask test client
        fund_name (str): The name of the fund to count applications
        expected_application_count (int):
        The expected number of applications within the fund

    """

    response = test_client.get(f"/fund/{fund_name}", follow_redirects=True)
    response_data = json.loads(response.data)
    assert len(response_data) == expected_application_count
