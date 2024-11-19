import json
from datetime import datetime, timedelta
from unittest import mock
from unittest.mock import ANY, MagicMock
from uuid import uuid4

import boto3
import pytest
from fsd_utils.services.aws_extended_client import SQSExtendedClient
from moto import mock_aws

from config import Config
from db import db
from db.models import Applications, ResearchSurvey
from db.queries.application import get_all_applications
from db.schemas import ApplicationSchema
from external_services.models.fund import Fund
from external_services.models.round import Round
from tests.helpers import (
    application_expected_data,
    count_fund_applications,
    expected_data_within_response,
    get_row_by_pk,
    key_list_to_regex,
    post_data,
    test_application_data,
    test_question_data,
)


@pytest.mark.unique_fund_round(True)
def test_create_application_is_successful(flask_test_client, unique_fund_round, mock_get_application_display_config):
    """
    GIVEN We have a functioning Application Store API
    WHEN we try to create an application
    THEN applications are created with the correct parameters
    """

    application_data_a1 = {
        "account_id": "usera",
        "fund_id": unique_fund_round[0],
        "round_id": unique_fund_round[0],
        "language": "en",
    }
    application_data_a2 = {
        "account_id": "usera",
        "fund_id": unique_fund_round[0],
        "round_id": unique_fund_round[0],
        "language": "cy",
    }
    response = post_data(flask_test_client, "/applications", application_data_a1)
    assert response.json()["language"] == "en"
    count_fund_applications(flask_test_client, unique_fund_round[0], 1)
    response = post_data(flask_test_client, "/applications", application_data_a2)
    assert response.json()["language"] == "cy"
    count_fund_applications(flask_test_client, unique_fund_round[0], 2)


@pytest.mark.parametrize(
    "requested_language,fund_supports_welsh,exp_language",
    [
        ("en", True, "en"),
        ("en", False, "en"),
        ("cy", True, "cy"),
        ("cy", False, "en"),
    ],
)
def test_create_application_language_choice(
    mocker, flask_test_client, fund_supports_welsh, requested_language, exp_language
):
    mock_fund = Fund(
        "Generated test fund no welsh",
        str(uuid4()),
        "TEST",
        "Testing fund",
        fund_supports_welsh,
        {"en": "English Fund Name", "cy": "Welsh Fund Name"},
        [],
    )
    mocker.patch("api.routes.application.routes.get_fund", return_value=mock_fund)
    blank_forms_mock = mocker.patch(
        "api.routes.application.routes.get_blank_forms",
        return_value=MagicMock(),
    )
    test_application = Applications(**application_expected_data[2])
    create_application_mock = mocker.patch(
        "api.routes.application.routes.create_application",
        return_value=test_application,
    )
    mocker.patch("api.routes.application.routes.add_new_forms")

    # Post one application and check it's created in the expected language
    application_data_a1 = {
        "account_id": "usera",
        "fund_id": "",
        "round_id": "",
        "language": requested_language,
    }
    response = post_data(flask_test_client, "/applications", application_data_a1)
    assert response.status_code == 201

    blank_forms_mock.assert_called_once_with(
        fund_id=ANY,
        round_id=ANY,
        language=exp_language,
    )
    create_application_mock.assert_called_once_with(
        account_id="usera",
        fund_id=ANY,
        round_id=ANY,
        language=exp_language,
    )


def test_create_application_creates_formatted_reference(
    flask_test_client, clear_test_data, mock_get_application_display_config
):
    """
    GIVEN We have a functioning Application Store API
    WHEN we try to create an application
    THEN a correctly formatted reference is created for the application
    """
    create_application_json = {
        "account_id": "usera",
        "fund_id": "47aef2f5-3fcb-4d45-acb5-f0152b5f03c4",
        "round_id": "c603d114-5364-4474-a0c4-c41cbf4d3bbd",
        "language": "en",
    }
    response = flask_test_client.post(
        "/applications",
        data=json.dumps(create_application_json),
        headers={"Content-Type": "application/json"},
        follow_redirects=True,
    )
    application = response.json()
    assert application["reference"].startswith("TEST-TEST")
    assert application["reference"][-6:].isupper()
    assert application["reference"][-6:].isalpha()


def test_create_application_creates_unique_reference(
    flask_test_client,
    mock_random_choices,
    clear_test_data,
    mock_get_application_display_config,
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
        "language": "en",
    }
    response = flask_test_client.post(
        "/applications",
        data=json.dumps(create_application_json),
        headers={"Content-Type": "application/json"},
        follow_redirects=True,
    )
    assert response.status_code == 201, f"First creation failed with status {response.status_code}: {response.content}"
    application = response.json()
    assert application["reference"] == "TEST-TEST-ABCDEF", f"Unexpected reference: {application['reference']}"

    # Second creation should fail
    response = flask_test_client.post(
        "/applications",
        data=json.dumps(create_application_json),
        headers={"Content-Type": "application/json"},
        follow_redirects=True,
    )

    assert response.status_code == 500, f"Expected status 500, but got {response.status_code}"
    error_data = response.json()

    assert "detail" in error_data, f"Expected 'detail' in error response, got: {error_data}"
    assert (
        "Max (10) tries exceeded for create application" in error_data["detail"]
    ), f"Unexpected error message: {error_data['detail']}"


@pytest.mark.apps_to_insert(test_application_data)
def test_get_all_applications(flask_test_client, app):
    """
    GIVEN We have a functioning Application Store API
    WHEN a request for applications with no set params
    THEN the response should return all applications
    """
    with app.app_context():
        serialiser = ApplicationSchema(exclude=["forms"])
        expected_data = [serialiser.dump(row) for row in get_all_applications()]
        expected_data_within_response(
            flask_test_client,
            "/applications",
            expected_data,
            exclude_regex_paths=key_list_to_regex(["round_name", "date_submitted", "last_edited"]),
        )


@pytest.mark.apps_to_insert([{"account_id": "unique_user", "language": "en"}])
@pytest.mark.unique_fund_round(True)
def test_get_applications_of_account_id(flask_test_client, seed_application_records, unique_fund_round, app):
    """
    GIVEN We have a functioning Application Store API
    WHEN a request for applications of account_id
    THEN the response should return applications of the account_id
    """
    with app.app_context():
        expected_data_within_response(
            flask_test_client,
            "/applications?account_id=unique_user",
            [seed_application_records[0].as_dict()],
            exclude_regex_paths=key_list_to_regex(
                [
                    "started_at",
                    "last_edited",
                    "date_submitted",
                    "round_name",
                    "forms",
                ]
            ),
        )


@pytest.mark.apps_to_insert([test_application_data[0]])
def test_update_section_of_application(flask_test_client, seed_application_records):
    """
    GIVEN We have a functioning Application Store API
    WHEN A put is made with a completed section
    THEN The section json should be updated to
    match the PUT'ed json and be marked as in-progress.
    """
    section_put = {
        "questions": test_question_data,
        "metadata": {
            "application_id": str(seed_application_records[0].id),
            "form_name": "declarations",
            "is_summary_page_submit": False,
        },
    }
    response = flask_test_client.put(
        "/applications/forms",
        json=section_put,
        follow_redirects=True,
    )
    assert 201 == response.status_code
    answer_found_list = [field["answer"] not in [None, ""] for field in response.json()["questions"][0]["fields"]]
    section_status = response.json()["status"]
    assert all(answer_found_list)
    assert section_status == "IN_PROGRESS"


@pytest.mark.apps_to_insert([test_application_data[0]])
def test_update_section_of_application_with_optional_field(flask_test_client, seed_application_records):
    """
    GIVEN We have a functioning Application Store API
    WHEN A put is made with a completed section
    THEN The section json should be updated to
    match the PUT'ed json and be marked as in-progress.
    """
    section_put = {
        "questions": [
            {
                "question": "Management case",
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
                    },
                ],
            }
        ],
        "metadata": {
            "application_id": str(seed_application_records[0].id),
            "form_name": "declarations",
            "is_summary_page_submit": False,
        },
    }
    response = flask_test_client.put(
        "/applications/forms",
        json=section_put,
        follow_redirects=True,
    )
    assert 201 == response.status_code
    section_status = response.json()["status"]
    assert section_status == "IN_PROGRESS"


@pytest.mark.apps_to_insert([test_application_data[0]])
def test_update_section_of_application_with_incomplete_answers(flask_test_client, seed_application_records):
    """
    GIVEN We have a functioning Application Store API
    WHEN A put is made with a completed section
    THEN The section json should be updated to
    match the PUT'ed json and be marked as complete.
    """
    section_put = {
        "questions": test_question_data,
        "metadata": {
            "application_id": str(seed_application_records[0].id),
            "form_name": "declarations",
        },
    }
    # Update an optional field to have no answer
    section_put["questions"][0]["fields"][2]["answer"] = ""
    expected_data = section_put.copy()
    # The whole section has been COMPLETED here so it will have a status of
    # COMPLETE not IN_PROGRESS
    expected_data.update({"status": "IN_PROGRESS"})
    # exclude_question_keys = ["category", "index", "id"]
    response = flask_test_client.put(
        "/applications/forms",
        json=section_put,
        follow_redirects=True,
    )
    assert 201 == response.status_code
    section_status = response.json()["status"]
    assert section_status == "IN_PROGRESS"


@pytest.mark.apps_to_insert([test_application_data[0]])
def test_get_application_by_application_id(flask_test_client, seed_application_records):
    """
    GIVEN We have a functioning Application Store API
    WHEN a GET /applications/<application_id> request is sent
    THEN the response should contain the application object
    """

    id = seed_application_records[0].id
    serialiser = ApplicationSchema()
    expected_data = serialiser.dump(seed_application_records[0])
    expected_data_within_response(
        flask_test_client,
        f"/applications/{id}",
        expected_data,
        exclude_regex_paths=key_list_to_regex(["reference", "started_at", "project_name", "forms"]),
        # Lists are annoying to deal with in deepdiff
        # especially when they contain dicts...so in this
        # instance we ignore them rather then write some
        # regex. (this recursively ignores 'forms')
        exclude_types=[list],
    )


@pytest.mark.apps_to_insert([test_application_data[0]])
def test_get_application_by_application_id_and_with_qa_file(flask_test_client, seed_application_records):
    """
    GIVEN We have a functioning Application Store API
    WHEN a GET /applications/<application_id> request is sent
    THEN the response should contain the application object
    """

    id = seed_application_records[0].id
    serialiser = ApplicationSchema()
    expected_data = serialiser.dump(seed_application_records[0])
    expected_data = {**expected_data, "questions_file": "KioqKioqKioqIEdlbmVyYXRlZCB0ZXN0IGZ1bmQgKioqKioqKioqKgo="}
    expected_data_within_response(
        flask_test_client,
        f"/applications/{id}?with_questions_file=true",
        expected_data,
        exclude_regex_paths=key_list_to_regex(["reference", "started_at", "project_name", "forms"]),
        # Lists are annoying to deal with in deepdiff
        # especially when they contain dicts...so in this
        # instance we ignore them rather then write some
        # regex. (this recursively ignores 'forms')
        exclude_types=[list],
    )


@pytest.mark.apps_to_insert(
    # element 1 has no lang set
    [test_application_data[1]]
)
def test_get_application_by_application_id_when_db_record_has_no_language_set(
    flask_test_client, seed_application_records
):
    """
    GIVEN We have a functioning Application Store API
    WHEN a GET /applications/<application_id> request is sent for an
        application with no language set (such as a pre-language
        functionality application)
    THEN the response should contain the application object with a default
        language of english ('en')
    """
    response = flask_test_client.get(
        f"/applications/{seed_application_records[0].id}",
        follow_redirects=True,
    )
    response_content = json.loads(response.content)
    assert response_content["language"] == "en"


@pytest.mark.apps_to_insert(
    # element 1 has no lang set
    [test_application_data[1]]
)
def test_get_application_by_application_id_when_db_record_has_no_language_set_and_with_qa_file(
    flask_test_client, seed_application_records
):
    """
    GIVEN We have a functioning Application Store API
    WHEN a GET /applications/<application_id> request is sent for an
        application with no language set (such as a pre-language
        functionality application)
    THEN the response should contain the application object with a default
        language of english ('en')
    """
    response = flask_test_client.get(
        f"/applications/{seed_application_records[0].id}?with_questions_file=true",
        follow_redirects=True,
    )
    response_content = json.loads(response.content)
    assert response_content["questions_file"] is not None


def testHealthcheckRoute(flask_test_client):
    expected_result = {
        "checks": [{"check_flask_running": "OK"}, {"check_db": "OK"}],
        "version": "abc123",
    }
    result = flask_test_client.get("/healthcheck")
    assert result.status_code == 200, "Unexpected status code"
    assert result.json() == expected_result, "Unexpected json body"


@pytest.mark.apps_to_insert([test_application_data[0]])
def test_update_section_of_application_changes_last_edited_field(flask_test_client, seed_application_records):
    """
    GIVEN We have a functioning Application Store API
    WHEN A put is made with a completed section
    THEN the section json.last_edited should be updated.
    """
    target_row = get_row_by_pk(Applications, seed_application_records[0].id)
    old_last_edited = target_row.last_edited
    form_name = "declarations"
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
            "application_id": str(target_row.id),
            "form_name": form_name,
        },
    }
    response = flask_test_client.put(
        "/applications/forms",
        json=section_put,
        follow_redirects=True,
    )
    assert 201 == response.status_code
    target_row = get_row_by_pk(Applications, seed_application_records[0].id)
    db.session.refresh(target_row)
    new_last_edited = target_row.last_edited
    assert new_last_edited != old_last_edited


@pytest.mark.apps_to_insert([test_application_data[0]])
def test_update_section_of_application_does_not_change_last_edited_field(flask_test_client, seed_application_records):
    """
    GIVEN We have a functioning Application Store API
    WHEN A put is made with a completed section
    THEN The section json.last_edited should not be updated.
    """
    old_last_edited = seed_application_records[0].last_edited
    section_put = {
        "questions": [],
        "metadata": {
            "application_id": str(seed_application_records[0].id),
            "form_name": "declarations",
        },
    }
    flask_test_client.put(
        "/applications/forms",
        json=section_put,
        follow_redirects=True,
    )
    app = get_row_by_pk(Applications, seed_application_records[0].id)
    new_last_edited = app.last_edited
    assert new_last_edited == old_last_edited


@pytest.mark.apps_to_insert([test_application_data[0]])
def test_update_project_name_of_application(flask_test_client, seed_application_records):
    """
    GIVEN We have a functioning Application Store API
    WHEN a put is made into the 'project information' section
     containing a project name field
    THEN the project name should be updated on the application.
    """
    old_project_name = seed_application_records[0].project_name
    new_project_name = "updated by unit test"
    form_name = "project-information"
    section_put = {
        "questions": [
            {
                "question": "About your project",
                "fields": [
                    {
                        "key": "TestFieldId",
                        "title": "Project name field",
                        "type": "text",
                        "answer": new_project_name,
                    },
                ],
            },
        ],
        "metadata": {
            "application_id": str(seed_application_records[0].id),
            "form_name": form_name,
        },
    }
    flask_test_client.put(
        "/applications/forms",
        json=section_put,
        follow_redirects=True,
    )
    target_row = get_row_by_pk(Applications, seed_application_records[0].id)
    db.session.refresh(target_row)
    assert target_row.project_name == new_project_name
    assert target_row.project_name != old_project_name


@pytest.mark.apps_to_insert([test_application_data[0]])
def test_complete_form(flask_test_client, seed_application_records):
    """
    GIVEN We have a functioning Application Store API
    WHEN A put is made with a completed section
    THEN The section json should be updated to
    match the PUT'ed json and be marked as in-progress.
    """
    section_put = {
        "questions": test_question_data,
        "metadata": {
            "application_id": str(seed_application_records[0].id),
            "form_name": "declarations",
            "isSummaryPageSubmit": True,
        },
    }
    response = flask_test_client.put(
        "/applications/forms",
        json=section_put,
        follow_redirects=True,
    )
    section_status = response.json()["status"]
    assert section_status == "COMPLETED"


@pytest.mark.apps_to_insert([test_application_data[0]])
def test_form_data_save_with_closed_round(flask_test_client, seed_application_records, mocker):
    """
    GIVEN We have a functioning Application Store API
    WHEN A put is made with a completed section,
    THEN The section JSON should be updated to
    match the PUT'ed JSON and be marked as in-progress.
    and if the round is closed then it will give a 301 to redirect the user to fund closure notification page
    """
    mocker.patch("db.queries.application.queries.get_round", new=generate_mock_round_closed)
    mocker.patch("db.queries.statuses.queries.get_round", new=generate_mock_round_closed)
    section_put = {
        "questions": test_question_data,
        "metadata": {
            "application_id": str(seed_application_records[0].id),
            "form_name": "declarations",
            "isSummaryPageSubmit": True,
        },
    }
    response = flask_test_client.put(
        "/applications/forms",
        json=section_put,
        follow_redirects=True,
    )
    assert response.status_code == 301


@pytest.mark.apps_to_insert([test_application_data[2]])
def test_put_returns_400_on_submitted_application(flask_test_client, _db, seed_application_records):
    """
    GIVEN We have a functioning Application Store API
    WHEN A there is an application with a status of SUBMITTED
    THEN any PUTs to the application data should return a 400 response
    """

    seed_application_records[0].status = "SUBMITTED"
    _db.session.add(seed_application_records[0])
    _db.session.commit()
    section_put = {
        "metadata": {
            "application_id": str(seed_application_records[0].id),
            "form_name": "datganiadau",
        },
        "questions": test_question_data,
    }

    response = flask_test_client.put(
        "/applications/forms",
        json=section_put,
        follow_redirects=True,
    )

    assert response.status_code == 400
    assert b"Not allowed to edit a submitted application." in response.content


@mock_aws
@pytest.mark.apps_to_insert([test_application_data[0]])
def test_successful_submitted_application(
    flask_test_client,
    mock_successful_submit_notification,
    _db,
    seed_application_records,
    mocker,
    mock_get_fund_data,
    mock_get_round,
):
    """
    GIVEN We have a functioning Application Store API
    WHEN an application is submitted
    THEN a 201 response is received in the correct format
    """
    with mock.patch("api.routes.application.routes.ApplicationsView._get_sqs_client") as mock_get_sqs_client:
        mock_get_sqs_client.return_value = _mock_aws_client()
        mocker.patch("db.queries.application.queries.list_files_by_prefix", new=lambda _: [])
        seed_application_records[0].status = "SUBMITTED"

        _db.session.add(seed_application_records[0])
        _db.session.commit()

        # mock successful notification
        response = flask_test_client.post(
            f"/applications/{seed_application_records[0].id}/submit",
            follow_redirects=True,
        )

        assert response.status_code == 201
        assert all(k in response.json() for k in ("id", "email", "reference", "eoi_decision"))


@pytest.mark.apps_to_insert([test_application_data[0]])
def test_stage_unsubmitted_application_to_queue_fails(
    flask_test_client, mock_successful_submit_notification, _db, seed_application_records, mocker, mock_get_fund_data
):
    """
    GIVEN We request to stage an unsubmitted application to the assessment queue
    WHEN an application is unsubmitted
    THEN a 400 response is received in the correct format
    """
    mocker.patch("db.queries.application.queries.list_files_by_prefix", new=lambda _: [])
    seed_application_records[0].status = "COMPLETED"

    _db.session.add(seed_application_records[0])
    _db.session.commit()

    # mock successful notification
    response = flask_test_client.post(
        f"/queue_for_assessment/{seed_application_records[0].id}",
        follow_redirects=True,
    )

    assert response.status_code == 400
    assert "Application must be submitted before it can be assessed" in response.text


@mock_aws
@pytest.mark.apps_to_insert([test_application_data[0]])
def test_stage_submitted_application_to_queue_fails(
    flask_test_client, mock_successful_submit_notification, _db, seed_application_records, mocker, mock_get_fund_data
):
    """
    GIVEN We request to stage an submitted application to the assessment queue
    WHEN an application is submitted
    THEN a 201 response is received in the correct format
    """
    with mock.patch("api.routes.queues.routes.QueueView._get_sqs_client") as mock_get_sqs_client:
        mock_get_sqs_client.return_value = _mock_aws_client()
        mocker.patch("db.queries.application.queries.list_files_by_prefix", new=lambda _: [])
        seed_application_records[0].status = "SUBMITTED"

        _db.session.add(seed_application_records[0])
        _db.session.commit()

        # mock successful notification
        response = flask_test_client.post(
            f"/queue_for_assessment/{seed_application_records[0].id}",
            follow_redirects=True,
        )

        assert response.status_code == 201
        assert "Message queued, message_id is:" in response.text


def _mock_aws_client():
    sqs_extended_client = SQSExtendedClient(
        aws_access_key_id="test_accesstoken",  # pragma: allowlist secret
        aws_secret_access_key="secret_key",  # pragma: allowlist secret
        region_name="us-east-1",
        large_payload_support=Config.AWS_MSG_BUCKET_NAME,
        always_through_s3=True,
        delete_payload_from_s3=True,
        logger=MagicMock(),
    )
    s3_connection = boto3.client(
        "s3",
        region_name="us-east-1",
        aws_access_key_id="test_accesstoken",  # pragma: allowlist secret
        aws_secret_access_key="secret_key",  # pragma: allowlist secret
    )
    sqs_connection = boto3.client(
        "sqs",
        region_name="us-east-1",
        aws_access_key_id="test_accesstoken",  # pragma: allowlist secret
        aws_secret_access_key="secret_key",  # pragma: allowlist secret
    )
    s3_connection.create_bucket(Bucket=Config.AWS_MSG_BUCKET_NAME)
    queue_response = sqs_connection.create_queue(QueueName="import-queue.fifo", Attributes={"FifoQueue": "true"})
    sqs_extended_client.sqs_client = sqs_connection
    sqs_extended_client.s3_client = s3_connection
    Config.AWS_SQS_IMPORT_APP_PRIMARY_QUEUE_URL = queue_response["QueueUrl"]
    return sqs_extended_client


def generate_mock_round_closed(fund_id: str, round_id: str) -> Round:
    return Round(
        title="Generated test round",
        id=round_id,
        fund_id=fund_id,
        short_name="TEST",
        opens=(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%S"),
        deadline=(datetime.now() - timedelta(days=5)).strftime("%Y-%m-%dT%H:%M:%S"),
        assessment_deadline=(datetime.now() + timedelta(days=10)).strftime("%Y-%m-%dT%H:%M:%S"),
        project_name_field_id="TestFieldId",
        contact_email="test@outlook.com",
        title_json={"en": "English title", "cy": "Welsh title"},
    )


def test_post_research_survey_data(flask_test_client, mocker):
    request_data = {
        "application_id": "123",
        "fund_id": "fund456",
        "round_id": "round789",
        "data": {"research_opt_in": "agree", "contact_name": "John Doe", "contact_email": "john@example.com"},
    }
    expected_survey_data = {
        **request_data,
        "id": 1,
        "date_submitted": "01-01-1000",
    }
    retrieved_survey_data = ResearchSurvey()
    retrieved_survey_data.id = expected_survey_data["id"]
    retrieved_survey_data.application_id = expected_survey_data["application_id"]
    retrieved_survey_data.fund_id = expected_survey_data["fund_id"]
    retrieved_survey_data.round_id = expected_survey_data["round_id"]
    retrieved_survey_data.data = expected_survey_data["data"]
    retrieved_survey_data.date_submitted = expected_survey_data["date_submitted"]

    mock_upsert_research_survey_data = mocker.patch(
        "api.routes.application.routes.upsert_research_survey_data", return_value=retrieved_survey_data
    )
    mock_update_statuses = mocker.patch("api.routes.application.routes.update_statuses")

    response = flask_test_client.post(
        "/application/research", data=json.dumps(request_data), headers={"Content-Type": "application/json"}
    )

    assert response.status_code == 201
    assert response.json() == expected_survey_data
    mock_upsert_research_survey_data.assert_called_once_with(
        application_id=request_data["application_id"],
        fund_id=request_data["fund_id"],
        round_id=request_data["round_id"],
        data=request_data["data"],
    )
    mock_update_statuses.assert_called_once_with(request_data["application_id"], form_name=None)


def test_get_research_survey_data(flask_test_client, mocker):
    application_id = "123"
    expected_survey_data = {
        "id": 1,
        "application_id": "123",
        "fund_id": "fund456",
        "round_id": "round789",
        "data": {"research_opt_in": "agree", "contact_name": "John Doe", "contact_email": "john@example.com"},
        "date_submitted": "01-01-1000",
    }
    retrieved_survey_data = ResearchSurvey()
    retrieved_survey_data.id = expected_survey_data["id"]
    retrieved_survey_data.application_id = expected_survey_data["application_id"]
    retrieved_survey_data.fund_id = expected_survey_data["fund_id"]
    retrieved_survey_data.round_id = expected_survey_data["round_id"]
    retrieved_survey_data.data = expected_survey_data["data"]
    retrieved_survey_data.date_submitted = expected_survey_data["date_submitted"]

    mock_retrieve_research_survey_data = mocker.patch(
        "api.routes.application.routes.retrieve_research_survey_data", return_value=retrieved_survey_data
    )

    response = flask_test_client.get(f"/application/research?application_id={application_id}")

    assert response.status_code == 200
    assert response.json() == expected_survey_data
    mock_retrieve_research_survey_data.assert_called_once_with(application_id)


def test_get_research_survey_data_not_found(flask_test_client, mocker):
    application_id = "app123"

    mock_retrieve_research_survey_data = mocker.patch(
        "api.routes.application.routes.retrieve_research_survey_data", return_value=None
    )

    response = flask_test_client.get(f"/application/research?application_id={application_id}")

    assert response.status_code == 404
    assert response.json() == {"code": 404, "message": f"Research survey data for {application_id} not found"}
    mock_retrieve_research_survey_data.assert_called_once_with(application_id)
