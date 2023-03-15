import pytest
from db.models import Applications
from db.models.application.enums import Status
from tests.helpers import get_all_rows
from tests.helpers import get_row_by_pk
from tests.helpers import test_application_data


@pytest.mark.apps_to_insert(test_application_data)
def test_get_application_statuses(client, seed_application_records, _db):
    response = client.get(
        "/applications/reporting/applications_statuses_data",
        follow_redirects=True,
    )
    assert (
        response.data
        == b"NOT_STARTED,IN_PROGRESS,SUBMITTED,COMPLETED\r\n3,0,0,0\r\n"
    )

    app = get_row_by_pk(Applications, seed_application_records[0].id)
    app.status = "IN_PROGRESS"
    _db.session.add(app)
    _db.session.commit()

    response = client.get(
        "/applications/reporting/applications_statuses_data",
        follow_redirects=True,
    )
    assert (
        response.data
        == b"NOT_STARTED,IN_PROGRESS,SUBMITTED,COMPLETED\r\n2,1,0,0\r\n"
    )


@pytest.mark.apps_to_insert([test_application_data[0]])
def test_get_applications_report(
    client, seed_application_records, add_org_data_for_reports
):

    application = get_row_by_pk(Applications, seed_application_records[0].id)
    application.status = Status.SUBMITTED

    response = client.get(
        "/applications/reporting/key_application_metrics",
        follow_redirects=True,
    )
    lines = response.data.splitlines()
    assert (
        "eoi_reference,organisation_name,organisation_type,asset_type,"
        + "geography,capital,revenue"
    ) == lines[0].decode("utf-8")
    fields = lines[1].decode("utf-8").split(",")
    assert "Test Org Name 1" == fields[1]
    assert "Test Reference Number" == fields[0]
    assert "W1A 1AA" == fields[4]


@pytest.mark.skip(
    reason="reinstate once we can filter on fund_id and round_id"
)
@pytest.mark.apps_to_insert(
    [test_application_data[0], test_application_data[1]]
)
def test_get_applications_report_query_param(
    client, seed_application_records, add_org_data_for_reports, _db
):
    all_apps = get_all_rows(Applications)
    for app in all_apps:
        app.status = "IN_PROGRESS"
    _db.session.add_all(all_apps)
    _db.session.commit()
    response = client.get(
        "/applications/reporting/key_application_metrics?status=IN_PROGRESS",
        follow_redirects=True,
    )
    lines = response.data.splitlines()
    assert 3 == len(lines)
    assert (
        "eoi_reference,organisation_name,organisation_type,asset_type,"
        + "geography,capital,revenue"
    ) == lines[0].decode("utf-8")
    for line in lines[1:]:
        fields = line.decode("utf-8").split(",")
        assert fields[1].startswith("Test Org Name ")
        assert "Test Reference Number" == fields[0]
        assert "W1A 1AA" == fields[4]
