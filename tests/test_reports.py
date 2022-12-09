from db.models import Applications
from db.models.application.enums import Status
from tests.helpers import get_random_row
from tests.helpers import post_data
from tests.helpers import post_test_applications, get_all_rows


def test_get_application_statuses(client):
    post_test_applications(client)
    response = client.get(
        "/applications/reporting/applications_statuses_data",
        follow_redirects=True,
    )
    assert (
        response.data
        == b"NOT_STARTED,IN_PROGRESS,SUBMITTED,COMPLETED\r\n3,0,0,0\r\n"
    )

    app = get_random_row(Applications)
    app.status = "IN_PROGRESS"

    response = client.get(
        "/applications/reporting/applications_statuses_data",
        follow_redirects=True,
    )
    assert (
        response.data
        == b"NOT_STARTED,IN_PROGRESS,SUBMITTED,COMPLETED\r\n2,1,0,0\r\n"
    )


def test_get_applications_report(client):
    application_data_1 = {
        "account_id": "usera",
        "fund_id": "47aef2f5-3fcb-4d45-acb5-f0152b5f03c4",
        "round_id": "c603d114-5364-4474-a0c4-c41cbf4d3bbd",
        "language": "en",
    }

    post_data(client, "/applications", application_data_1)

    application = get_random_row(Applications)
    sections_put_en = [
        {
            "questions": [
                {
                    "question": "About your organisation",
                    "fields": [
                        {
                            "key": "YdtlQZ",
                            "title": "Organisation Name",
                            "type": "text",
                            "answer": "Test Organisation Name",
                        },
                        {
                            "key": "WWWWxy",
                            "title": "EOI Reference",
                            "type": "text",
                            "answer": "Test Reference Number",
                        },
                    ],
                },
            ],
            "metadata": {
                "application_id": application.id,
                "form_name": "organisation-information",
                "is_summary_page_submit": False,
            },
        },
        {
            "questions": [
                {
                    "question": "Address",
                    "fields": [
                        {
                            "key": "yEmHpp",
                            "title": "Address",
                            "type": "text",
                            "answer": "BBC, W1A 1AA",
                        },
                    ],
                },
            ],
            "metadata": {
                "application_id": application.id,
                "form_name": "project-information",
                "is_summary_page_submit": False,
            },
        },
    ]

    for section in sections_put_en:
        client.put(
            "/applications/forms",
            json=section,
            follow_redirects=True,
        )
    application.status = Status.SUBMITTED

    response = client.get(
        "/applications/reporting/key_application_metrics",
        follow_redirects=True,
    )

    assert "Test Organisation Name" in response.data.decode("utf-8")
    assert "Test Reference Number" in response.data.decode("utf-8")
    assert "W1A 1AA" in response.data.decode("utf-8")


def test_get_applications_report_query_param(client):
    post_test_applications(client)
    apps = get_all_rows(Applications)
    app_one = apps[0]
    app_two = apps[1]
    sections_put_app_one = [
        {
            "questions": [
                {
                    "question": "About your organisation",
                    "fields": [
                        {
                            "key": "YdtlQZ",
                            "title": "Organisation Name",
                            "type": "text",
                            "answer": "Test Organisation Name",
                        },
                        {
                            "key": "WWWWxy",
                            "title": "EOI Reference",
                            "type": "text",
                            "answer": "Test Reference Number",
                        },
                    ],
                },
            ],
            "metadata": {
                "application_id": app_one.id,
                "form_name": "organisation-information",
                "is_summary_page_submit": False,
            },
        },
        {
            "questions": [
                {
                    "question": "Address",
                    "fields": [
                        {
                            "key": "yEmHpp",
                            "title": "Address",
                            "type": "text",
                            "answer": "BBC, W1A 1AA",
                        },
                    ],
                },
            ],
            "metadata": {
                "application_id": app_one.id,
                "form_name": "project-information",
                "is_summary_page_submit": False,
            },
        },
    ]
    sections_put_app_two = [
        {
            "questions": [
                {
                    "question": "About your organisation",
                    "fields": [
                        {
                            "key": "YdtlQZ",
                            "title": "Organisation Name",
                            "type": "text",
                            "answer": "Test Organisation Name 2",
                        },
                        {
                            "key": "WWWWxy",
                            "title": "EOI Reference",
                            "type": "text",
                            "answer": "Test Reference Number 2",
                        },
                    ],
                },
            ],
            "metadata": {
                "application_id": app_two.id,
                "form_name": "organisation-information",
                "is_summary_page_submit": False,
            },
        },
        {
            "questions": [
                {
                    "question": "Address",
                    "fields": [
                        {
                            "key": "yEmHpp",
                            "title": "Address",
                            "type": "text",
                            "answer": "BBC, BA2 1AA",
                        },
                    ],
                },
            ],
            "metadata": {
                "application_id": app_two.id,
                "form_name": "project-information",
                "is_summary_page_submit": False,
            },
        },
    ]

    for section in sections_put_app_one:
        client.put(
            "/applications/forms",
            json=section,
            follow_redirects=True,
        )
    for section in sections_put_app_two:
        client.put(
            "/applications/forms",
            json=section,
            follow_redirects=True,
        )
    app_one.status = Status.IN_PROGRESS
    app_two.status = Status.IN_PROGRESS
    apps[2].status = Status.IN_PROGRESS

    response = client.get(
        "/applications/reporting/key_application_metrics?status=IN_PROGRESS",
        follow_redirects=True,
    )
    report_reponse = response.data.decode("utf-8")
    assert "organisation_name" in report_reponse
    assert "Test Organisation Name" in report_reponse
    assert "Test Organisation Name 2" in report_reponse
    assert "Test Reference Number" in report_reponse
    assert "W1A 1AA" in report_reponse
    assert "BA2 1AA" in report_reponse
    