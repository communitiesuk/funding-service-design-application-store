from config.envs.unit_testing import UnitTestingConfig
from scripts.send_application_on_closure import (
    send_incomplete_applications_after_deadline,
)  # noqa
from tests.helpers import post_data


class TestSendAppOnClosure:
    def test_send_apps_no_apps(self, mocker):
        fund_id = UnitTestingConfig.COF_FUND_ID
        round_id = UnitTestingConfig.COF_ROUND_2_ID

        with (
            mocker.patch(
                "scripts.send_application_on_closure.get_fund_round",
                return_value={"deadline": "2022-01-01 12:00:00"},
            )
        ):

            result = send_incomplete_applications_after_deadline(
                fund_id, round_id
            )
            assert 0 == result, "Unexpected result number"

    def test_send_apps_one_to_send(self, mocker, client):
        fund_id = UnitTestingConfig.COF_FUND_ID
        round_id = UnitTestingConfig.COF_ROUND_2_ID
        post_data(
            client,
            "/applications",
            {
                "account_id": "usera",
                "date_submitted": "null",
                "fund_id": "47aef2f5-3fcb-4d45-acb5-f0152b5f03c4",
                "language": "en",
                "project_name": "unsubmitted project 1",
                "reference": "COF-R2W2-LYDANK",
                "round_id": "c603d114-5364-4474-a0c4-c41cbf4d3bbd",
            },
        )

        with (
            mocker.patch(
                "scripts.send_application_on_closure.get_fund_round",
                return_value={
                    "deadline": "2022-12-01 12:00:00",
                    "round_name": "COF R2W2",
                },
            )
        ):

            result = send_incomplete_applications_after_deadline(
                fund_id, round_id
            )
            assert 1 == result, "Unexpected result number"

    def test_send_apps_before_deadline(self, mocker):
        fund_id = UnitTestingConfig.COF_FUND_ID
        round_id = UnitTestingConfig.COF_ROUND_2_ID

        with (
            mocker.patch(
                "scripts.send_application_on_closure.get_fund_round",
                return_value={"deadline": "2025-01-01 12:00:00"},
            )
        ):

            result = send_incomplete_applications_after_deadline(
                fund_id, round_id
            )
            assert -1 == result, "Unexpected result number"
