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
        response.data == b"NOT_STARTED,IN_PROGRESS,SUBMITTED,COMPLETED\r\n3,0,0,0\r\n"
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
        response.data == b"NOT_STARTED,IN_PROGRESS,SUBMITTED,COMPLETED\r\n2,1,0,0\r\n"
    )


user_lang = {
    "account_id": "usera",
    "language": "en",
}

user_lang_cy = {
    "account_id": "userw",
    "language": "cy",
}


@pytest.mark.fund_round_config(
    {
        "funds": [
            {"rounds": [{"applications": [{**user_lang_cy}]}]},
            {
                "rounds": [
                    {"applications": [{**user_lang}]},
                    {"applications": [{**user_lang_cy}, {**user_lang}]},
                ]
            },
        ]
    }
)
@pytest.mark.parametrize(
    "fund_idx,round_idx,expected_in_progress",
    [
        # (None, None, 4),
        (0, 0, 1),
        (0, None, 1),
        (1, 0, 1),
        (1, 1, 2),
        (1, None, 3),
    ],
)
def test_get_application_statuses_query_param(
    fund_idx,
    round_idx,
    expected_in_progress,
    client,
    seed_data_multiple_funds_rounds,
):

    fund_id = (
        seed_data_multiple_funds_rounds[fund_idx].fund_id
        if fund_idx is not None
        else ""
    )
    round_id = (
        seed_data_multiple_funds_rounds[fund_idx].round_ids[round_idx][0]
        if round_idx is not None
        else ""
    )

    url = (
        "/applications/reporting/applications_statuses_data?fund_id="
        + f"{fund_id}&round_id={round_id}"
    )

    response = client.get(
        url,
    )
    lines = response.data.splitlines()
    assert 2 == len(lines)
    assert lines[0] == b"NOT_STARTED,IN_PROGRESS,SUBMITTED,COMPLETED"
    assert expected_in_progress == int(lines[1].decode("utf-8").split(",")[1])


@pytest.mark.parametrize(
    "language,expected_org_name,expected_address,ref_number",
    [
        ("en", "Test Org Name 1", "W1A 1AA", "Test Reference Number"),
        ("cy", "Test Org Name 2cy", "CF10 3NQ", "Test Reference Number Welsh"),
    ],
)
@pytest.mark.parametrize("include_application_id", (True, False))
@pytest.mark.fund_round_config(
    {
        "funds": [
            {"rounds": [{"applications": [{**user_lang}, {**user_lang_cy}]}]},
        ]
    }
)
def test_get_applications_report(
    client,
    include_application_id,
    language,
    expected_org_name,
    expected_address,
    ref_number,
    seed_data_multiple_funds_rounds,
):
    application_id = (
        seed_data_multiple_funds_rounds[0].round_ids[0].application_ids[0]
        if language == "en"
        else seed_data_multiple_funds_rounds[0].round_ids[0].application_ids[1]
    )
    application = get_row_by_pk(
        Applications,
        application_id,
    )
    application.status = Status.SUBMITTED
    url = "/applications/reporting/key_application_metrics" + (
        f"/{str(application.id)}"
        if include_application_id
        else (
            f"?fund_id={seed_data_multiple_funds_rounds[0].fund_id}"
            + "&round_id="
            + f"{seed_data_multiple_funds_rounds[0].round_ids[0].round_id}"
        )
    )
    response = client.get(
        url,
        follow_redirects=True,
    )
    assert 200 == response.status_code
    lines = response.data.splitlines()
    assert 2 == len(lines)
    assert (
        "eoi_reference,organisation_name,organisation_type,asset_type,"
        + "geography,capital,revenue"
    ) == lines[0].decode("utf-8")
    fields = lines[1].decode("utf-8").split(",")
    assert expected_org_name == fields[1]
    assert ref_number == fields[0]
    assert expected_address == fields[4]


@pytest.mark.fund_round_config(
    {
        "funds": [
            {"rounds": [{"applications": [{**user_lang}, {**user_lang_cy}]}]},
        ]
    }
)
def test_get_applications_report_query_param(client, seed_data_multiple_funds_rounds):

    response = client.get(
        "/applications/reporting/key_application_metrics?status=IN_PROGRESS&"
        + f"fund_id={seed_data_multiple_funds_rounds[0].fund_id}&round_id="
        + f"{seed_data_multiple_funds_rounds[0].round_ids[0].round_id}",
        follow_redirects=True,
    )
    raw_lines = response.data.splitlines()
    assert len(raw_lines) == 3

    line1, line2, line3 = [line.decode("utf-8") for line in response.data.splitlines()]
    assert (
        line1
        == "eoi_reference,organisation_name,organisation_type,asset_type,"
        "geography,capital,revenue"
    )

    field1, field2, _, _, field5, _, _ = line2.split(",")
    assert field1 == "Test Reference Number"
    assert field2.startswith("Test Org Name ")
    assert field5 == "W1A 1AA"

    field1, field2, _, _, field5, _, _ = line3.split(",")
    assert field1 == "Test Reference Number Welsh"
    assert field2.startswith("Test Org Name 2cy")
    assert field5 == "CF10 3NQ"
