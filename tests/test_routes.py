import json
from operator import itemgetter

from db.models.applications import ApplicationTestMethods
from tests.helpers import application_expected_data
from tests.helpers import count_fund_applications
from tests.helpers import expected_data_within_response
from tests.helpers import key_list_to_regex
from tests.helpers import post_data
from tests.helpers import post_test_applications


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
    count_fund_applications(client, "fund-a", expected_length_fund_a)

    # Post first Fund B application and check length
    application_data_b1 = {
        "account_id": "userb",
        "fund_id": "fund-b",
        "round_id": "summer",
    }
    post_data(client, "/applications", application_data_b1)

    expected_length_fund_b = 1
    count_fund_applications(client, "fund-b", expected_length_fund_b)

    # Post second Fund B application and check length
    application_data_b2 = {
        "account_id": "userc",
        "fund_id": "fund-b",
        "round_id": "summer",
    }
    post_data(client, "/applications", application_data_b2)

    expected_length_fund_b = 2
    count_fund_applications(client, "fund-b", expected_length_fund_b)


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
    expected_data = list(
        filter(
            lambda app_dict: app_dict["account_id"] == account_id_to_filter,
            application_expected_data,
        )
    )

    expected_data_within_response(
        client,
        "/applications?account_id=userb",
        expected_data,
        exclude_regex_paths=key_list_to_regex(["id", "started_at"]),
    )


def test_update_section_of_application(client):
    """
    GIVEN We have a functioning Application Store API
    WHEN A put is made with a completed section
    THEN The section json should be updated to
    match the PUT'ed json and be marked as complete.
    """
    post_test_applications(client)

    random_app = ApplicationTestMethods.get_random_app()
    random_application_id = random_app.id

    section_put = {
        "questions": [
            {
                "question": "About your organisation",
                "fields": [
                    {
                        "key": "application-name",
                        "title": "Applicant name",
                        "type": "text",
                        "answer": "Coolio",
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
                        "answer": "Wow",
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
            "application_id": str(random_application_id),
            "form_name": "declarations"
        },
    }

    response = client.put(
        "/applications/forms",
        data=json.dumps(section_put),
        follow_redirects=True,
    )

    answer_found_list = [
        field["answer"] not in [None, ""]
        for field in response.json["questions"][0]["fields"]
    ]

    section_status = response.json["status"]

    assert all(answer_found_list)
    assert section_status == "COMPLETED"


def test_update_section_of_application_with_incomplete_answers(
    client,
):
    """
        GIVEN We have a functioning Application Store API
        WHEN A put is made with a completed section
        THEN The section json should be updated to
        match the PUT'ed json and be marked as complete.
    """
    post_test_applications(client)

    random_app = ApplicationTestMethods.get_random_app()
    random_application_id = random_app.id

    section_put = {
        "questions": [
            {
                "question": "About your organisation",
                "fields": [
                    {
                        "key": "application-name",
                        "title": "Applicant name",
                        "type": "text",
                        "answer": "Coolio",
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
                        # NOT GIVEN!!
                        "answer": "",
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
            "application_id": str(random_application_id),
            "form_name": "declarations",    
        },
    }
    expected_data = section_put.copy()

    # The whole section has been submit here so it will have a status of
    # COMPLETE not IN_PROGRESS
    expected_data.update({"status": "IN_PROGRESS"})

    # exclude_question_keys = ["category", "index", "id"]

    response = client.put(
        "/applications/forms",
        data=json.dumps(section_put),
        follow_redirects=True,
    )

    print(response.json)

    section_status = response.json["status"]

    assert section_status == "IN_PROGRESS"


def test_get_application_by_application_id(client):
    """
    GIVEN We have a functioning Application Store API
    WHEN a GET /applications/<application_id> request is sent
    THEN the response should contain the application object
    """

    post_test_applications(client)

    random_app = ApplicationTestMethods.get_random_app()

    random_id = random_app.id

    expected_data = {**random_app.as_dict(), "forms": []}

    expected_data_within_response(
        client,
        f"/applications/{random_id}",
        expected_data,
        exclude_regex_paths=key_list_to_regex(
            ["started_at", "project_name", "forms"]
        ),
        # Lists are annoying to deal with in deepdiff
        # especially when they contain dicts...so in this
        # instance we ignore them rather then write some
        # regex. (this recursively ignores 'forms')
        exclude_types=[list],
    )


def testHealthcheckRoute(client):
    expected_result = {"checks": [{"check_flask_running": "OK"}]}
    result = client.get("/healthcheck")
    assert result.status_code == 200, "Unexpected status code"
    assert result.json == expected_result, "Unexpected json body"
