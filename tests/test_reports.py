from db.models.applications import ApplicationTestMethods
from db.models.status import Status
from tests.helpers import post_data
from tests.helpers import post_test_applications


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

    app = ApplicationTestMethods.get_random_app()
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

    application = ApplicationTestMethods.get_random_app()
    application.status = Status.SUBMITTED
    section_put_en = {
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
    }

    client.put(
        "/applications/forms",
        json=section_put_en,
        follow_redirects=True,
    )

    response = client.get(
        "/applications/reporting/key_application_metrics",
        follow_redirects=True,
    )

    assert "Test Organisation Name" in response.data.decode("utf-8")
    assert "Test Reference Number" in response.data.decode("utf-8")
