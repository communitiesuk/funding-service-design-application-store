import json
from slugify import slugify
from typing import List


def expected_data_within_get_response(
    test_client, endpoint: str, expected_data
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

    if isinstance(expected_data, List):
        for idx, data in enumerate(expected_data):
            if isinstance(data, dict):
                if isinstance(response_data, List):
                    for key, value in response_data[idx].items():
                        assert value == data[key]
                elif isinstance(response_data, dict):
                    raise Exception("Expecting response json to be a list")
            else:
                assert response_data[idx] == expected_data[idx]
    elif isinstance(expected_data, dict):
        if isinstance(response_data, dict):
            for key, value in response_data.items():
                assert value == expected_data[key]
        else:
            raise Exception("Expecting response json to be a dict")


def put_response_return_200(test_client, endpoint):
    """
    Given a endpoint
    check to see if returns a 200 success response

    Args:
        test_client: A flask test client
        endpoint (str): The PUT request endpoint

    """

    response = test_client.put(endpoint, follow_redirects=True)
    assert response.status_code == 200


def post_data(test_client, endpoint: str, data: dict):
    """Given an endpoint and data, check to see if response contains expected data

    Args:
        test_client: A flask test client
        endpoint (str): The POST request endpoint
        data (dict): The content to post to the endpoint provided
    """

    response = test_client.post(
        endpoint, data=json.dumps(data),
        content_type="application/json",
        follow_redirects=True
    )
    print(response.data)


def put_data(test_client, endpoint: str, data: dict):
    """Given an endpoint and data, check to see if response contains expected data

    Args:
        test_client: A flask test client
        endpoint (str): The POST request endpoint
        data (dict): The content to post to the endpoint provided
    """

    test_client.put(
        endpoint,
        data=json.dumps(post_data),
        content_type="application/json",
        follow_redirects=True
    )


def count_fund_applications(
    test_client, fund_id: str, expected_application_count
):
    """
    Given a fund_id, check the number of applications for it

    Args:
        test_client: A flask test client
        fund_id (str): The id of the fund to count applications
        expected_application_count (int):
        The expected number of applications for the fund

    """
    fund_applications_endpoint = f"/applications/search?fund_id={fund_id}"
    response = test_client.get(fund_applications_endpoint, follow_redirects=True)
    response_data = json.loads(response.data)
    error_message = "Response from " + fund_applications_endpoint + " found " + str(len(response_data)) \
                    + " items, but expected " + str(expected_application_count)
    assert len(response_data) == expected_application_count, error_message
