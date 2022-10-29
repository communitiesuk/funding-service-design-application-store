import json

import pytest
from db.models.aggregate_functions import get_round_name
from db.models.applications import ApplicationError
from db.models.applications import Applications
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
        "fund_id": "47aef2f5-3fcb-4d45-acb5-f0152b5f03c4",
        "round_id": "c603d114-5364-4474-a0c4-c41cbf4d3bbd",
    }
    post_data(client, "/applications", application_data_a1)
    expected_length_fund_a = 1
    count_fund_applications(
        client, "47aef2f5-3fcb-4d45-acb5-f0152b5f03c4", expected_length_fund_a
    )
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


def test_create_application_creates_formatted_reference(client):
    """
    GIVEN We have a functioning Application Store API
    WHEN we try to create an application
    THEN a correctly formatted reference is created for the application
    """
    create_application_json = {
        "account_id": "usera",
        "fund_id": "47aef2f5-3fcb-4d45-acb5-f0152b5f03c4",
        "round_id": "c603d114-5364-4474-a0c4-c41cbf4d3bbd",
    }
    response = client.post(
        "/applications",
        data=json.dumps(create_application_json),
        content_type="application/json",
        follow_redirects=True,
    )
    application = response.json
    assert application["reference"].startswith("COF-SUM-")
    assert application["reference"][-6:].isupper()
    assert application["reference"][-6:].isalpha()


def test_create_application_creates_unique_reference(
    client, mock_random_choices
):
    """
    GIVEN We have a functioning Application Store API
    WHEN we try to create an application
    THEN a unique application_reference is created for the application
    """
    create_application_json = {
        "account_id": "usera",
        "fund_id": "47aef2f5-3fcb-4d45-acb5-f0152b5f03c4",
        "round_id": "c603d114-5364-4474-a0c4-c41cbf4d3bbd",
    }
    response = client.post(
        "/applications",
        data=json.dumps(create_application_json),
        content_type="application/json",
        follow_redirects=True,
    )
    application = response.json
    assert application["reference"] == "COF-SUM-ABCDEF"

    with pytest.raises(ApplicationError) as ex_info:
        client.post(
            "/applications",
            data=json.dumps(create_application_json),
            content_type="application/json",
            follow_redirects=True,
        )
    assert str(ex_info.value).startswith(
        "Max (10) tries exceeded for create application with application key"
        " ABCDEF"
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
        exclude_regex_paths=key_list_to_regex(
            [
                "id",
                "reference",
                "started_at",
                "project_name",
                "last_edited",
                "date_submitted",
            ]
        ),
    )


def test_update_section_of_application(client):
    """
    GIVEN We have a functioning Application Store API
    WHEN A put is made with a completed section
    THEN The section json should be updated to
    match the PUT'ed json and be marked as in-progress.
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
            },
            {
                "question": "About your organisation",
                "fields": [
                    {
                        "key": "data",
                        "title": "Applicant name",
                        "type": "text",
                        "answer": "cool",
                    },
                ],
            },
            {
                "question": "About your organisation",
                "fields": [
                    {
                        "key": "data",
                        "title": "Applicant job",
                        "type": "text",
                        "answer": "cool",
                    },
                ],
            },
        ],
        "metadata": {
            "application_id": str(random_application_id),
            "form_name": "declarations",
            "is_summary_page_submit": False,
        },
    }
    response = client.put(
        "/applications/forms",
        json=section_put,
        follow_redirects=True,
    )
    answer_found_list = [
        field["answer"] not in [None, ""]
        for field in response.json["questions"][0]["fields"]
    ]
    section_status = response.json["status"]
    assert all(answer_found_list)
    assert section_status == "IN_PROGRESS"


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
            },
            {
                "question": "About your organisation",
                "fields": [
                    {
                        "key": "data",
                        "title": "Applicant name",
                        "type": "text",
                        "answer": "cool",
                    },
                ],
            },
        ],
        "metadata": {
            "application_id": str(random_application_id),
            "form_name": "declarations",
        },
    }
    expected_data = section_put.copy()
    # The whole section has been COMPLETED here so it will have a status of
    # COMPLETE not IN_PROGRESS
    expected_data.update({"status": "IN_PROGRESS"})
    # exclude_question_keys = ["category", "index", "id"]
    response = client.put(
        "/applications/forms",
        json=section_put,
        follow_redirects=True,
    )
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
    round_name = get_round_name(random_app.fund_id, random_app.round_id)
    expected_data = {
        **random_app.as_dict(),
        "round_name": round_name,
        "forms": [],
    }
    expected_data_within_response(
        client,
        f"/applications/{random_id}",
        expected_data,
        exclude_regex_paths=key_list_to_regex(
            ["reference", "started_at", "project_name", "forms"]
        ),
        # Lists are annoying to deal with in deepdiff
        # especially when they contain dicts...so in this
        # instance we ignore them rather then write some
        # regex. (this recursively ignores 'forms')
        exclude_types=[list],
    )


def testHealthcheckRoute(client):
    expected_result = {
        "checks": [{"check_flask_running": "OK"}, {"check_db": "OK"}]
    }
    result = client.get("/healthcheck")
    assert result.status_code == 200, "Unexpected status code"
    assert result.json == expected_result, "Unexpected json body"


def test_update_section_of_application_changes_last_edited_field(client):
    """
    GIVEN We have a functioning Application Store API
    WHEN A put is made with a completed section
    THEN the section json.last_edited should be updated.
    """
    post_test_applications(client)
    random_app = ApplicationTestMethods.get_random_app()
    random_application_id = random_app.id
    old_last_edited = random_app.last_edited
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
            "form_name": "declarations",
        },
    }
    client.put(
        "/applications/forms",
        json=section_put,
        follow_redirects=True,
    )
    new_last_edited = random_app.last_edited
    assert new_last_edited != old_last_edited


def test_update_section_of_application_does_not_change_last_edited_field(
    client,
):
    """
    GIVEN We have a functioning Application Store API
    WHEN A put is made with a completed section
    THEN The section json.last_edited should not be updated.
    """
    post_test_applications(client)
    random_app = ApplicationTestMethods.get_random_app()
    random_application_id = random_app.id
    old_last_edited = random_app.last_edited
    section_put = {
        "questions": [],
        "metadata": {
            "application_id": str(random_application_id),
            "form_name": "declarations",
        },
    }
    client.put(
        "/applications/forms",
        json=section_put,
        follow_redirects=True,
    )
    new_last_edited = random_app.last_edited
    assert new_last_edited == old_last_edited


def test_update_project_name_of_application(client):
    """
    GIVEN We have a functioning Application Store API
    WHEN A put is made with a completed section
    THEN the section json.last_edited should be updated.
    """
    post_test_applications(client)
    random_app = ApplicationTestMethods.get_random_app()
    random_application_id = random_app.id
    old_project_name = random_app.project_name
    section_put = {
        "questions": [
            {
                "question": "About your project",
                "fields": [
                    {
                        "key": "gScdbf",
                        "title": (
                            "Have you been given funding through the Community"
                            " Ownership Fund before?"
                        ),
                        "type": "list",
                        "answer": True,
                    }
                ],
            },
            {
                "question": "About your project",
                "fields": [
                    {
                        "key": "IrIYcA",
                        "title": "Describe your previous project",
                        "type": "text",
                        "answer": "fcbcfbxf",
                    },
                    {
                        "key": "TFdnGq",
                        "title": "Amount of funding received",
                        "type": "text",
                        "answer": "4255",
                    },
                ],
            },
            {
                "question": "About your project",
                "fields": [
                    {
                        "key": "KAgrBz",
                        "title": "Project name",
                        "type": "text",
                        "answer": "YESS ONEEEE",
                    },
                    {
                        "key": "wudRxx",
                        "title": (
                            "Tell us how the asset is currently being used, or"
                            " how it has been used before, and why it's"
                            " important to the community"
                        ),
                        "type": "text",
                        "answer": "dcfcdc",
                    },
                    {
                        "key": "TlGjXb",
                        "title": (
                            "Explain why the asset is at risk of being lost to"
                            " the community, or why it has already been lost"
                        ),
                        "type": "text",
                        "answer": "czcxzc",
                    },
                    {
                        "key": "GCjCse",
                        "title": (
                            "Give a brief summary of your project, including"
                            " what you hope to achieve"
                        ),
                        "type": "text",
                        "answer": "xzczcxzxcz",
                    },
                ],
            },
        ],
        "metadata": {
            "application_id": str(random_application_id),
            "form_name": "project-information",
        },
    }
    client.put(
        "/applications/forms",
        json=section_put,
        follow_redirects=True,
    )
    new_project_name = random_app.project_name
    assert new_project_name != old_project_name


def test_complete_form(client):
    """
    GIVEN We have a functioning Application Store API
    WHEN A put is made with a completed section
    THEN The section json should be updated to
    match the PUT'ed json and be marked as in-progress.
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
            },
            {
                "question": "About your organisation",
                "fields": [
                    {
                        "key": "data",
                        "title": "Applicant name",
                        "type": "text",
                        "answer": "cool",
                    },
                ],
            },
            {
                "question": "About your organisation",
                "fields": [
                    {
                        "key": "data",
                        "title": "Applicant job",
                        "type": "text",
                        "answer": "cool",
                    },
                ],
            },
        ],
        "metadata": {
            "application_id": str(random_application_id),
            "form_name": "declarations",
            "isSummaryPageSubmit": True,
        },
    }
    response = client.put(
        "/applications/forms",
        json=section_put,
        follow_redirects=True,
    )
    section_status = response.json["status"]
    assert section_status == "COMPLETED"


def test_put_returns_400_on_submitted_application(client, db_session):

    post_test_applications(client)
    """
    GIVEN We have a functioning Application Store API
    WHEN A there is an application with a status of SUBMITTED
    THEN any PUTs to the application data should return a 400 response
    """
    import random

    application_list = db_session.query(Applications).all()
    random_app = random.choice(application_list)
    random_application_id = random_app.id
    random_app.status = "SUBMITTED"
    db_session.add(random_app)
    db_session.commit()
    section_put = {
        "metadata": {
            "application_id": random_application_id,
            "form_name": "declarations",
        },
        "questions": [{"TEST": "TEST"}],
    }

    response = client.put(
        "/applications/forms",
        json=section_put,
        follow_redirects=True,
    )

    assert response.status_code == 400
    assert b"Not allowed to edit a submitted application." in response.data
