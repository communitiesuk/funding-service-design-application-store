import pytest
from db.models import Applications
from db.models.application.enums import Status
from tests.helpers import get_row_by_pk
from tests.helpers import test_application_data


@pytest.mark.apps_to_insert(test_application_data)
def test_get_application_statuses_csv(client, seed_application_records, _db):
    response = client.get(
        "/applications/reporting/applications_statuses_data",
        follow_redirects=True,
    )

    lines = response.data.decode("utf-8").split("\r\n")
    assert lines[0] == "fund_id,round_id,NOT_STARTED,IN_PROGRESS,COMPLETED,SUBMITTED"
    assert (
        f"{test_application_data[0]['fund_id']},{test_application_data[0]['round_id']},1,0,0,0"
        in lines
    )
    assert (
        f"{test_application_data[1]['fund_id']},{test_application_data[1]['round_id']},1,0,0,0"
        in lines
    )
    assert (
        f"{test_application_data[2]['fund_id']},{test_application_data[2]['round_id']},1,0,0,0"
        in lines
    )

    app = get_row_by_pk(Applications, seed_application_records[0].id)
    app.status = "IN_PROGRESS"
    _db.session.add(app)
    _db.session.commit()

    response = client.get(
        "/applications/reporting/applications_statuses_data",
        follow_redirects=True,
    )

    lines = response.data.decode("utf-8").split("\r\n")
    assert lines[0] == "fund_id,round_id,NOT_STARTED,IN_PROGRESS,COMPLETED,SUBMITTED"
    assert (
        f"{test_application_data[0]['fund_id']},{test_application_data[0]['round_id']},0,1,0,0"
        in lines
    )
    assert (
        f"{test_application_data[1]['fund_id']},{test_application_data[1]['round_id']},1,0,0,0"
        in lines
    )
    assert (
        f"{test_application_data[2]['fund_id']},{test_application_data[2]['round_id']},1,0,0,0"
        in lines
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
            {
                "rounds": [
                    {
                        "applications": [
                            {**user_lang_cy},
                            {**user_lang_cy},
                            {**user_lang},
                        ]
                    },
                    {
                        "applications": [
                            {**user_lang},
                        ]
                    },
                    {"applications": []},
                ]
            },
            {
                "rounds": [
                    {
                        "applications": [
                            {**user_lang_cy},
                            {**user_lang_cy},
                        ]
                    }
                ]
            },
        ]
    }
)
@pytest.mark.parametrize(
    "fund_idx, round_idx, exp_not_started, exp_in_progress, exp_submitted,"
    " exp_completed",
    [
        ([0, 1], [], 0, 5, 0, 1),
        ([0], [], 0, 3, 0, 1),
        ([1], [], 0, 2, 0, 0),
        ([0], [1, 2], 0, 1, 0, 0),
        ([0], [2], 0, 0, 0, 0),
        ([], [0], 0, 2, 0, 1),
    ],
)
def test_get_application_statuses_json_multi_fund(
    fund_idx,
    round_idx,
    exp_not_started,
    exp_in_progress,
    exp_submitted,
    exp_completed,
    client,
    seed_data_multiple_funds_rounds,
    _db,
    mock_get_round,
):
    app = get_row_by_pk(Applications, seed_data_multiple_funds_rounds[0][1][0][1][0])
    app.status = "COMPLETED"
    _db.session.add(app)
    _db.session.commit()
    fund_ids = [seed_data_multiple_funds_rounds[idx][0] for idx in fund_idx]
    fund_params = ["fund_id=" + str(id) for id in fund_ids]
    round_ids = [seed_data_multiple_funds_rounds[0][1][idx][0] for idx in round_idx]
    round_params = ["round_id=" + str(id) for id in round_ids]
    url = (
        "/applications/reporting/applications_statuses_data?"
        + f"format=json&{'&'.join(fund_params)}&{'&'.join(round_params)}"
    )
    response = client.get(url, follow_redirects=True)
    assert response.status_code == 200
    result = response.json
    assert result
    funds = result["metrics"]
    for fund_id in fund_ids:
        assert (
            len([fund["fund_id"] for fund in funds if fund["fund_id"] == fund_id]) == 1
        )
        total_ip = 0
        total_ns = 0
        total_c = 0
        total_s = 0
        for f in funds:
            total_ns += sum(
                [r["application_statuses"]["NOT_STARTED"] for r in f["rounds"]]
            )
            total_ip += sum(
                [r["application_statuses"]["IN_PROGRESS"] for r in f["rounds"]]
            )
            total_c += sum(
                [r["application_statuses"]["COMPLETED"] for r in f["rounds"]]
            )
            total_s += sum(
                [r["application_statuses"]["SUBMITTED"] for r in f["rounds"]]
            )
        assert total_ns == exp_not_started
        assert total_ip == exp_in_progress
        assert total_c == exp_completed
        assert total_s == exp_submitted


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
        + "geography,capital,revenue,organisation_name_nstf"
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
def test_get_applications_report_query_param(
    client, seed_data_multiple_funds_rounds, mock_get_round
):

    response = client.get(
        "/applications/reporting/key_application_metrics?status=IN_PROGRESS&"
        + f"fund_id={seed_data_multiple_funds_rounds[0].fund_id}&round_id="
        + f"{seed_data_multiple_funds_rounds[0].round_ids[0].round_id}",
        follow_redirects=True,
    )

    raw_lines = response.data.splitlines()
    assert len(raw_lines) == 3

    lines = [line.decode("utf-8") for line in response.data.splitlines()]
    assert (
        lines[0]
        == "eoi_reference,organisation_name,organisation_type,asset_type,"
        "geography,capital,revenue,organisation_name_nstf"
    )

    for line in lines[1:]:

        field1, field2, _, _, field5, _, _, _ = line.split(",")
        if field1 == "Test Reference Number":
            assert field2.startswith("Test Org Name ")
            assert field5 == "W1A 1AA"
        elif field1 == "Test Reference Number Welsh":
            assert field2.startswith("Test Org Name 2cy")
            assert field5 == "CF10 3NQ"
        else:
            assert 1 == 0, "Unexpected value for first column"
