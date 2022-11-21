from db.models.applications import ApplicationTestMethods
from db.models.status import Status
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
    post_test_applications(client)

    application = ApplicationTestMethods.get_random_app()
    application.status = Status.SUBMITTED
    section_put = {
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
        json=section_put,
        follow_redirects=True,
    )

    response = client.get(
        "/applications/reporting/key_application_metrics",
        follow_redirects=True,
    )

    assert "Test Organisation Name" in response.data.decode("utf-8")
