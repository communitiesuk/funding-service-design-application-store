from db.models.applications import ApplicationTestMethods
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
