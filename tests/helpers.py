import json

from deepdiff import DeepDiff


def expected_data_within_response(
    test_client,
    endpoint: str,
    expected_data,
    method="get",
    data=None,
    exclude_regex_paths=None,
):
    """
    Given a endpoint and expected content,
    check to see if response contains expected data

    Args:
        test_client: A flask test client
        endpoint (str): The request endpoint
        method (str): The method of the request
        data: The data to post/put if required
        expected_data: The content we expect to find
        exclude_regex_paths: paths to exclude from diff

    """
    if method == "put":
        print(endpoint)
        print(data)
        response = test_client.put(endpoint, data=data, follow_redirects=True)
        print(expected_data)
        print(response.data)
    elif method == "post":
        response = test_client.post(endpoint, data=data, follow_redirects=True)
    else:
        response = test_client.get(endpoint, follow_redirects=True)
    response_data = json.loads(response.data)

    diff = DeepDiff(
        expected_data, response_data, exclude_regex_paths=exclude_regex_paths
    )

    error_message = "Expected data does not match response: " + str(diff)
    assert diff == {}, error_message


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
        endpoint,
        data=json.dumps(data),
        content_type="application/json",
        follow_redirects=True,
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
        follow_redirects=True,
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
    fund_applications_endpoint = f"/applications?fund_id={fund_id}"
    response = test_client.get(
        fund_applications_endpoint, follow_redirects=True
    )
    response_data = json.loads(response.data)
    error_message = (
        "Response from "
        + fund_applications_endpoint
        + " found "
        + str(len(response_data))
        + " items, but expected "
        + str(expected_application_count)
    )
    assert len(response_data) == expected_application_count, error_message
