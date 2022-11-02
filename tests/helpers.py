import json
import os
import re
import urllib
from typing import List

from config import Config
from deepdiff import DeepDiff


def local_api_call(endpoint: str, params: dict = None, method: str = "get"):
    api_data_json = os.path.join(
        Config.FLASK_ROOT,
        "tests",
        "api_data",
        method.lower() + "_endpoint_data.json",
    )
    fp = open(api_data_json)
    api_data = json.load(fp)
    fp.close()
    query_params = "_"
    if params:
        query_params = urllib.parse.urlencode(params)
    if method.lower() == "post":
        if endpoint in api_data:
            post_dict = api_data.get(endpoint)
            if query_params in post_dict:
                return post_dict.get(query_params)
            else:
                return post_dict.get("_default")
    else:
        if params:
            endpoint = f"{endpoint}?{query_params}"
        if endpoint in api_data:
            return api_data.get(endpoint)


def expected_data_within_response(
    test_client,
    endpoint: str,
    expected_data,
    method="get",
    data=None,
    exclude_regex_paths=None,
    **kwargs,
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
        response = test_client.put(endpoint, data=data, follow_redirects=True)
    elif method == "post":
        response = test_client.post(endpoint, data=data, follow_redirects=True)
    else:
        response = test_client.get(endpoint, follow_redirects=True)
    response_data = json.loads(response.data)
    diff = DeepDiff(
        expected_data,
        response_data,
        exclude_regex_paths=exclude_regex_paths,
        **kwargs,
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
    test_client.post(
        endpoint,
        data=json.dumps(data),
        content_type="application/json",
        follow_redirects=True,
    )


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


def post_test_applications(client):
    application_data_1 = {
        "account_id": "usera",
        "fund_id": "47aef2f5-3fcb-4d45-acb5-f0152b5f03c4",
        "round_id": "c603d114-5364-4474-a0c4-c41cbf4d3bbd",
        "language": "en",
    }
    application_data_2 = {
        "account_id": "userb",
        "fund_id": "fund-b",
        "round_id": "summer",
        "language": "null",
    }
    application_data_3 = {
        "account_id": "userc",
        "fund_id": "funding-service-design",
        "round_id": "spring",
        "language": "cy",
    }
    post_data(client, "/applications", application_data_1)
    post_data(client, "/applications", application_data_2)
    post_data(client, "/applications", application_data_3)


application_post_data = [
    {
        "account_id": "usera",
        "fund_id": "47aef2f5-3fcb-4d45-acb5-f0152b5f03c4",
        "round_id": "c603d114-5364-4474-a0c4-c41cbf4d3bbd",
        "language": "en",
    },
    {
        "account_id": "userb",
        "fund_id": "fund-b",
        "round_id": "summer",
        "language": "null",
    },
    {
        "account_id": "userc",
        "fund_id": "funding-service-design",
        "round_id": "spring",
        "language": "cy",
    },
]

application_expected_data = [
    {
        "status": "NOT_STARTED",
        "project_name": "project_name not set",
        "date_submitted": None,
        "started_at": "2022-05-20 14:47:12",
        "last_edited": None,
        **application_data,
    }
    for application_data in application_post_data
]


def key_list_to_regex(
    exclude_keys: List[str] = [
        "id",
        "reference",
        "started_at",
        "project_name",
        "last_edited",
        "date_submitted",
    ]
):
    exclude_regex_path_strings = [
        rf"root\[\d+\]\['{key}'\]" for key in exclude_keys
    ]

    exclude_regex_path_strings_nested = [
        rf"root\[\d+\]\['{key}'\]\[\d+\]" for key in exclude_keys
    ]

    regex_paths = (
        exclude_regex_path_strings + exclude_regex_path_strings_nested
    )
    return [re.compile(regex_string) for regex_string in regex_paths]
