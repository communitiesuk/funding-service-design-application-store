from config.envs.unit_testing import UnitTestingConfig
from scripts.send_application_on_closure import (
    send_incomplete_applications_after_deadline,
)  # noqa


class TestSendAppOnClosure:
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
