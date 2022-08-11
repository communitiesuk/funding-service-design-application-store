import json
from operator import itemgetter
import re
from db.models.applications import ApplicationTestMethods

from tests.helpers import count_fund_applications, key_list_to_regex, post_test_applications, application_expected_data
from tests.helpers import expected_data_within_response
from tests.helpers import post_data


def test_create_application_is_successful(client):
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
    post_data(client, "/applications", application_data_a1)

    expected_length_fund_a = 1
    count_fund_applications(
        client, "fund-a", expected_length_fund_a
    )

    # Post first Fund B application and check length
    application_data_b1 = {
        "account_id": "userb",
        "fund_id": "fund-b",
        "round_id": "summer",
    }
    post_data(client, "/applications", application_data_b1)

    expected_length_fund_b = 1
    count_fund_applications(
        client, "fund-b", expected_length_fund_b
    )

    # Post second Fund B application and check length
    application_data_b2 = {
        "account_id": "userc",
        "fund_id": "fund-b",
        "round_id": "summer",
    }
    post_data(client, "/applications", application_data_b2)

    expected_length_fund_b = 2
    count_fund_applications(
        client, "fund-b", expected_length_fund_b
    )


def test_get_all_applications(client):
    """
    GIVEN We have a functioning Application Store API
    WHEN a request for applications with no set params
    THEN the response should return all applications
    """
    post_test_applications(client)
    expected_data = application_expected_data

    expected_data_within_response(
        client,
        "/applications",
        expected_data,
        exclude_regex_paths=key_list_to_regex(),
    )


def test_get_applications_sorted_by_rev_account_id(client):
    """
    GIVEN We have a functioning Application Store API
    WHEN a request for applications reverse sorted by account_id
    THEN the response should return applications in the requested order
    """
    post_test_applications(client)
    raw_expected_data = application_expected_data
    order_by = "account_id"
    order_rev = 1
    sorted_matching_applications_jsons = sorted(
                raw_expected_data,
                key=itemgetter(order_by),
                reverse=order_rev,
            )

    expected_data_within_response(
        client,
        f"/applications?order_by={order_by}&order_rev={order_rev}",
        sorted_matching_applications_jsons,
        exclude_regex_paths=key_list_to_regex(),
    )


def test_get_applications_of_account_id(client):
    """
    GIVEN We have a functioning Application Store API
    WHEN a request for applications of account_id
    THEN the response should return applications of the account_id
    """
    post_test_applications(client)
    account_id_to_filter = "userb"
    expected_data = list(filter(lambda app_dict : app_dict["account_id"] == account_id_to_filter, application_expected_data))

    expected_data_within_response(
        client,
        "/applications?account_id=userb",
        expected_data,
        exclude_regex_paths=key_list_to_regex(["id", "started_at"]),
    )


def test_update_section_of_application(client):
    """
    GIVEN We have a functioning Application Store API
    WHEN a request for applications of account_id
    THEN the response should return applications of the account_id
    """
    account_applications_response = client.get(
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
    # The whole section has been submit here so it will have a status of
    # COMPLETE not IN_PROGRESS
    expected_data.update({"section_name": section_name, "status": "COMPLETED"})
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
        client,
        "/applications/sections",
        expected_data,
        method="put",
        data=json.dumps(section_put),
        exclude_regex_paths=exclude_regex_paths,
    )


def test_update_section_of_application_with_incomplete_answers(
    client,
):
    """
    GIVEN We have a functioning Application Store API
    WHEN a request for applications of account_id
    THEN the response should return applications of the account_id
    """
    account_applications_response = client.get(
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
                        "answer": None,
                    },
                    {
                        "key": "applicant-email",
                        "title": "Email",
                        "type": "text",
                        "answer": "a@example.com",
                    },
                    {
                        "key": "applicant-telephone-number",
                        "title": "Phone",
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
    # The whole section has not been submit here (missing answer) so it
    # will have a status of IN_PROGRESS
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
        client,
        "/applications/sections",
        expected_data,
        method="put",
        data=json.dumps(section_put),
        exclude_regex_paths=exclude_regex_paths,
    )


def test_get_application_by_application_id(client):
    """
    GIVEN We have a functioning Application Store API
    WHEN a GET /applications/<application_id> request is sent
    THEN the response should contain the application object
    """

    post_test_applications(client)

    random_app = ApplicationTestMethods.get_random_app()

    random_id = random_app.id

    expected_data = {**random_app.as_dict(), 'forms' : []}

    expected_data_within_response(
        client,
        f"/applications/{random_id}",
        expected_data,
        exclude_regex_paths=key_list_to_regex(["started_at", "project_name", "forms"]),
        # Lists are annoying to deal with in deepdiff
        # especially when they contain dicts...so in this
        # instance we ignore them rather then write some
        # regex. (this recursively ignores 'forms')
        exclude_types=[list]
    )
