import pytest
from db.models import Applications
from db.models.application.enums import Status
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


fund_1_id = "47aef2f5-3fcb-4d45-1111-f0152b5f03c4"
fund_2_id = "47aef2f5-3fcb-4d45-2222-f0152b5f03c4"
round_1_id = "47aef2f5-3fcb-1111-1111-f0152b5f03c4"
round_2_id = "47aef2f5-3fcb-2222-2222-f0152b5f03c4"
round_3_id = "47aef2f5-3fcb-3333-2222-f0152b5f03c4"
user_lang = {
    "account_id": "usera",
    "language": "en",
}


@pytest.mark.parametrize(
    "fund_id,round_id,expected_not_started",
    [
        (fund_1_id, round_1_id, 1),
        (fund_2_id, round_2_id, 1),
        (fund_2_id, round_3_id, 2),
        (fund_2_id, "", 3),
        ("", "", 4),
    ],
)
@pytest.mark.apps_to_insert(
    [
        {"fund_id": fund_1_id, "round_id": round_1_id, **user_lang},
        {"fund_id": fund_2_id, "round_id": round_2_id, **user_lang},
        {"fund_id": fund_2_id, "round_id": round_3_id, **user_lang},
        {"fund_id": fund_2_id, "round_id": round_3_id, **user_lang},
    ]
)
# @pytest.mark.preserve_test_data(True)
def test_get_application_statuses_query_param(
    fund_id, round_id, expected_not_started, client, seed_application_records
):

    response = client.get(
        f"/applications/reporting/applications_statuses_data?fund_id={fund_id}"
        + f"&round_id={round_id}",
    )

    lines = response.data.splitlines()
    assert 2 == len(lines)
    assert lines[0] == b"NOT_STARTED,IN_PROGRESS,SUBMITTED,COMPLETED"
    assert expected_not_started == int(lines[1].decode("utf-8").split(",")[0])


@pytest.mark.parametrize("include_application_id", (True, False))
@pytest.mark.apps_to_insert([test_application_data[0]])
def test_get_applications_report(
    client,
    include_application_id,
    seed_application_records,
    add_org_data_for_reports,
):

    application = get_row_by_pk(Applications, seed_application_records[0].id)
    application.status = Status.SUBMITTED

    response = client.get(
        "/applications/reporting/key_application_metrics"
        + f"{'/' + str(application.id) if include_application_id else ''}",
        follow_redirects=True,
    )
    lines = response.data.splitlines()
    assert 2 == len(lines)
    assert (
        "eoi_reference,organisation_name,organisation_type,asset_type,"
        + "geography,capital,revenue"
    ) == lines[0].decode("utf-8")
    fields = lines[1].decode("utf-8").split(",")
    assert "Test Org Name 1" == fields[1]
    assert "Test Reference Number" == fields[0]
    assert "W1A 1AA" == fields[4]


@pytest.mark.apps_to_insert(
    [test_application_data[0], test_application_data[1]]
)
@pytest.mark.unique_fund_round(True)
def test_get_applications_report_query_param(
    client,
    seed_application_records,
    add_org_data_for_reports,
    _db,
    unique_fund_round,
):
    for app in seed_application_records:
        app.status = "IN_PROGRESS"
    _db.session.add_all(seed_application_records)
    _db.session.commit()
    response = client.get(
        "/applications/reporting/key_application_metrics?status=IN_PROGRESS&"
        + f"fund_id={unique_fund_round[0]}&round_id={unique_fund_round[1]}",
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
