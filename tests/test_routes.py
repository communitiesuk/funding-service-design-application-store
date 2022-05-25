import json
import re

from tests.helpers import count_fund_applications
from tests.helpers import expected_data_within_response
from tests.helpers import post_data


def test_create_application_is_successful(flask_test_client):
    """
    GIVEN We have a functioning Application Store API
    WHEN we try to create an application
    THEN applications are created with the correct parameters
    """

    # Post one Fund A application and check length
    application_data_a1 = {
        "account_id": "usera",
        "fund_id": "fund-a",
        "round_id": "summer",
    }
    post_data(flask_test_client, "/applications", application_data_a1)

    expected_length_fund_a = 1
    count_fund_applications(
        flask_test_client, "fund-a", expected_length_fund_a
    )

    # Post first Fund B application and check length
    application_data_b1 = {
        "account_id": "userb",
        "fund_id": "fund-b",
        "round_id": "summer",
    }
    post_data(flask_test_client, "/applications", application_data_b1)

    expected_length_fund_b = 1
    count_fund_applications(
        flask_test_client, "fund-b", expected_length_fund_b
    )

    # Post second Fund B application and check length
    application_data_b2 = {
        "account_id": "userc",
        "fund_id": "fund-b",
        "round_id": "summer",
    }
    post_data(flask_test_client, "/applications", application_data_b2)

    expected_length_fund_b = 2
    count_fund_applications(
        flask_test_client, "fund-b", expected_length_fund_b
    )


def test_get_all_applications(flask_test_client):
    """
    GIVEN We have a functioning Application Store API
    WHEN a request for applications with no set params
    THEN the response should return all applications
    """
    expected_data = [
        {
            "id": "uuidv4",
            "status": "NOT_STARTED",
            "account_id": "test-user",
            "fund_id": "funding-service-design",
            "round_id": "summer",
            "project_name": None,
            "date_submitted": None,
            "started_at": "2022-05-20 14:47:12",
            "last_edited": None,
        },
        {
            "id": "string",
            "status": "NOT_STARTED",
            "account_id": "usera",
            "fund_id": "fund-a",
            "round_id": "summer",
            "project_name": None,
            "date_submitted": None,
            "started_at": "2022-12-25 00:00:00",
            "last_edited": None,
        },
        {
            "id": "string",
            "status": "NOT_STARTED",
            "account_id": "userb",
            "fund_id": "fund-b",
            "round_id": "summer",
            "project_name": "",
            "date_submitted": None,
            "started_at": "2022-12-25 00:00:00",
            "last_edited": None,
        },
        {
            "id": "string",
            "status": "NOT_STARTED",
            "account_id": "userc",
            "fund_id": "fund-b",
            "round_id": "summer",
            "project_name": "",
            "date_submitted": None,
            "started_at": "2022-12-25 00:00:00",
            "last_edited": None,
        },
    ]
    exclude_keys = ["id", "started_at", "project_name"]
    exclude_regex_path_strings = [
        rf"root\[\d+\]\['{key}'\]" for key in exclude_keys
    ]
    exclude_regex_paths = [
        re.compile(regex_string) for regex_string in exclude_regex_path_strings
    ]
    expected_data_within_response(
        flask_test_client,
        "/applications",
        expected_data,
        exclude_regex_paths=exclude_regex_paths,
    )


# TODO: Add individual search filter endpoint tests below
# def test_get_applications_by_status_completed(flask_test_client):
#     """
#     GIVEN We have a functioning Application Store API
#     WHEN a request for applications with a given status
#     THEN the response should only contain the applications that
#     have that status
#     """
#     expected_data = [
#         {
#             "id": "uuidv4",
#             "status": "COMPLETED",
#             "fund_id": "test-fund-name",
#             "round_id": "spring",
#             "date_submitted": "2021-12-24 00:00:00",
#             "assessment_deadline": "2022-08-28 00:00:00",
#         }
#     ]
#
#     expected_data_within_get_response(
#         flask_test_client,
#         "/applications/search?status_only=completed",
#         expected_data,
#     )


# def test_search_endpoint_get_applications_by_status(flask_test_client):
#     """
#     GIVEN We have a functioning Application Store API
#     WHEN a request for applications with a given status
#     THEN the response should only contain the applications that
#     have that status
#     """
#     expected_data = [
#         {
#             "id": "uuidv4-2",
#             "status": "NOT_STARTED",
#             "assessment_deadline": "2022-08-28 00:00:00",
#             "fund_id": "slugified_test_fund_name"
#         }
#     ]
#
#     expected_data_within_get_response(
#         flask_test_client,
#         "/search"
#         "?status_only=not%20started",
#         expected_data,
#     )


# def test_get_applications_by_id_contains(flask_test_client):
#     """
#     GIVEN We have a functioning Application Store API
#     WHEN a request for applications whose id's contain a given string
#     THEN the response should only contain the applications that
#     have ids that contain that string
#     """
#     expected_data = [
#         {
#             "id": "uuidv4-2",
#             "status": "NOT_STARTED",
#             "fund_id": "test-fund-name",
#             "round_id": "spring",
#             "date_submitted": "2022-12-25 00:00:00",
#             "assessment_deadline": "2022-08-28 00:00:00",
#         }
#     ]
#
#     expected_data_within_get_response(
#         flask_test_client,
#         "/applications/search?id_contains=v4-2",
#         expected_data,
#     )


# def test_get_fund_applications_by_time_period(flask_test_client):
#     """
#     GIVEN We have a functioning Application Store API
#     WHEN a request for applications for a fund within a given time period
#     THEN the response should only contain the applications for the fund
#     that fall within the time period
#     """
#     expected_data = [
#         {
#             "id": "uuidv4-2",
#             "status": "NOT_STARTED",
#             "fund_id": "test-fund-name",
#             "round_id": "spring",
#             "date_submitted": "2022-12-25 00:00:00",
#             "assessment_deadline": "2022-08-28 00:00:00",
#         }
#     ]
#
#     expected_data_within_get_response(
#         flask_test_client,
#         "/applications/search"
#         "?fund_id=test-fund-name&datetime_start=2022-01-01&datetime_end=2022-12-28",
#         expected_data,
#     )


def test_get_applications_sorted_by_rev_account_id(flask_test_client):
    """
    GIVEN We have a functioning Application Store API
    WHEN a request for applications reverse sorted by account_id
    THEN the response should return applications in the requested order
    """
    expected_data = [
        {
            "id": "string",
            "status": "NOT_STARTED",
            "account_id": "userc",
            "fund_id": "fund-b",
            "round_id": "summer",
            "project_name": "",
            "date_submitted": None,
            "started_at": "2022-12-25 00:00:00",
            "last_edited": None,
        },
        {
            "id": "string",
            "status": "NOT_STARTED",
            "account_id": "userb",
            "fund_id": "fund-b",
            "round_id": "summer",
            "project_name": "",
            "date_submitted": None,
            "started_at": "2022-12-25 00:00:00",
            "last_edited": None,
        },
        {
            "id": "string",
            "status": "NOT_STARTED",
            "account_id": "usera",
            "fund_id": "fund-a",
            "round_id": "summer",
            "project_name": "",
            "date_submitted": None,
            "started_at": "2022-12-25 00:00:00",
            "last_edited": None,
        },
        {
            "id": "uuidv4",
            "status": "NOT_STARTED",
            "account_id": "test-user",
            "fund_id": "funding-service-design",
            "round_id": "summer",
            "project_name": None,
            "date_submitted": None,
            "started_at": "2022-05-20 14:47:12",
            "last_edited": None,
        },
    ]
    exclude_keys = ["id", "started_at", "project_name"]
    exclude_regex_path_strings = [
        rf"root\[\d+\]\['{key}'\]" for key in exclude_keys
    ]
    exclude_regex_paths = [
        re.compile(regex_string) for regex_string in exclude_regex_path_strings
    ]
    expected_data_within_response(
        flask_test_client,
        "/applications?order_by=account_id&order_rev=1",
        expected_data,
        exclude_regex_paths=exclude_regex_paths,
    )


def test_get_applications_of_account_id(flask_test_client):
    """
    GIVEN We have a functioning Application Store API
    WHEN a request for applications of account_id
    THEN the response should return applications of the account_id
    """
    expected_data = [
        {
            "id": "string",
            "status": "NOT_STARTED",
            "account_id": "userb",
            "fund_id": "fund-b",
            "round_id": "summer",
            "project_name": "",
            "date_submitted": None,
            "started_at": "2022-12-25 00:00:00",
            "last_edited": None,
        }
    ]
    exclude_keys = ["id", "started_at"]
    exclude_regex_path_strings = [
        rf"root\[\d+\]\['{key}'\]" for key in exclude_keys
    ]
    exclude_regex_paths = [
        re.compile(regex_string) for regex_string in exclude_regex_path_strings
    ]
    expected_data_within_response(
        flask_test_client,
        "/applications?account_id=userb",
        expected_data,
        exclude_regex_paths=exclude_regex_paths,
    )


def test_update_section_of_application(flask_test_client):
    """
    GIVEN We have a functioning Application Store API
    WHEN a request for applications of account_id
    THEN the response should return applications of the account_id
    """
    account_applications_response = flask_test_client.get(
        "/applications?account_id=userb"
    )
    account_applications = account_applications_response.get_json()
    application_id = account_applications[0]["id"]
    section_put = {
        "name": "about-your-org",
        "questions": [
            {
                "question": "About your organisation",
                "fields": [
                    {
                        "key": "application-name",
                        "title": "Applicant name",
                        "type": "text",
                        "answer": "User A",
                    },
                    {
                        "key": "applicant-email",
                        "title": "Email",
                        "type": "text",
                        "answer": "a@example.com",
                    },
                    {
                        "key": "applicant-telephone-number",
                        "title": "Telephone number",
                        "type": "text",
                        "answer": "01234 567 890",
                    },
                    {
                        "key": "applicant-website",
                        "title": "Website",
                        "type": "text",
                        "answer": "www.example.com",
                    },
                ],
            }
        ],
        "metadata": {
            "paymentSkipped": "false",
            "application_id": application_id,
        },
    }
    expected_data = section_put.copy()
    section_name = expected_data.pop("name")
    expected_data.update(
        {"section_name": section_name, "status": "IN_PROGRESS"}
    )
    exclude_keys = ["id", "started_at"]
    exclude_regex_path_strings = [
        rf"root\[\d+\]\['{key}'\]" for key in exclude_keys
    ]
    exclude_question_keys = ["status", "category", "index"]
    exclude_regex_path_strings.extend(
        [
            rf"root\['questions']\[\d+\]\['{key}'\]"
            for key in exclude_question_keys
        ]
    )
    exclude_metadata_keys = ["application_id"]
    exclude_regex_path_strings.extend(
        [rf"root\['metadata']\['{key}'\]" for key in exclude_metadata_keys]
    )
    exclude_regex_paths = [
        re.compile(regex_string) for regex_string in exclude_regex_path_strings
    ]
    expected_data_within_response(
        flask_test_client,
        "/applications/sections",
        expected_data,
        method="put",
        data=json.dumps(section_put),
        exclude_regex_paths=exclude_regex_paths,
    )


def test_get_application_by_application_id(flask_test_client):
    """
    GIVEN We have a functioning Application Store API
    WHEN a GET /applications/<application_id> request is sent
    THEN the response should contain the application object
    """

    expected_data = {
        "id": "uuidv4",
        "account_id": "test-user",
        "status": "NOT_STARTED",
        "fund_id": "funding-service-design",
        "round_id": "summer",
        "project_name": None,
        "date_submitted": None,
        "started_at": "2022-05-20 14:47:12",
        "last_edited": None,
        "sections": [],
    }

    exclude_keys = ["sections"]
    exclude_regex_path_strings = [rf"root\['{key}'\]" for key in exclude_keys]
    exclude_regex_paths = [
        re.compile(regex_string) for regex_string in exclude_regex_path_strings
    ]
    expected_data_within_response(
        flask_test_client,
        "/applications/uuidv4",
        expected_data,
        exclude_regex_paths=exclude_regex_paths,
    )
