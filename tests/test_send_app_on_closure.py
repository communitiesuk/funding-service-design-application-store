import pytest
from config.envs.unit_testing import UnitTestingConfig
from pytest import raises
from scripts.send_application_on_closure import (
    send_incomplete_applications_after_deadline,
)  # noqa
from tests.helpers import test_application_data


class TestSendAppOnClosure:
    @pytest.mark.apps_to_insert(
        [
            {
                "account_id": "bad_id",
                "language": "en",
            }
        ]
    )
    @pytest.mark.unique_fund_round(True)
    def test_send_apps_bad_account_id(
        self, mocker, client, seed_application_records, unique_fund_round
    ):

        mocker.patch(
            "scripts.send_application_on_closure.get_fund_round",
            return_value={
                "deadline": "2022-12-01 12:00:00",
                "round_name": "COF R2W2",
            },
        )

        with raises(LookupError):
            send_incomplete_applications_after_deadline(
                unique_fund_round[0], unique_fund_round[1], True
            )

        result = send_incomplete_applications_after_deadline(
            unique_fund_round[0], unique_fund_round[1], False
        )
        assert result == 0

    @pytest.mark.apps_to_insert([])
    @pytest.mark.unique_fund_round(True)
    def test_send_apps_no_apps(
        self,
        mocker,
        seed_application_records,
        unique_fund_round,
        mock_get_fund,
    ):
        fund_id = unique_fund_round[0]
        round_id = unique_fund_round[1]

        mocker.patch(
            "scripts.send_application_on_closure.get_fund_round",
            return_value={"deadline": "2022-01-01 12:00:00"},
        )

        result = send_incomplete_applications_after_deadline(
            fund_id, round_id, True
        )
        assert 0 == result, "Unexpected result number"

    @pytest.mark.apps_to_insert([test_application_data[0]])
    @pytest.mark.unique_fund_round(True)
    def test_send_apps_send_emails_is_false(
        self, mocker, seed_application_records, unique_fund_round
    ):
        mocker.patch(
            "scripts.send_application_on_closure.get_fund_round",
            return_value={"deadline": "2022-01-01 12:00:00"},
        )

        result = send_incomplete_applications_after_deadline(
            unique_fund_round[0], unique_fund_round[1], False
        )
        assert 1 == result

    @pytest.mark.apps_to_insert([test_application_data[0]])
    @pytest.mark.unique_fund_round(True)
    def test_send_apps_one_to_send_not_started(
        self, mocker, client, seed_application_records, unique_fund_round
    ):

        mocker.patch(
            "scripts.send_application_on_closure.get_fund_round",
            return_value={
                "deadline": "2022-12-01 12:00:00",
                "round_name": "COF R2W2",
            },
        )

        result = send_incomplete_applications_after_deadline(
            unique_fund_round[0], unique_fund_round[1], True
        )
        assert 1 == result

    @pytest.mark.apps_to_insert([test_application_data[0]])
    @pytest.mark.unique_fund_round(True)
    def test_send_apps_one_to_send_in_progress(
        self, mocker, client, seed_application_records, _db, unique_fund_round
    ):

        seed_application_records[0].status = "IN_PROGRESS"
        _db.session.add(seed_application_records[0])
        _db.session.commit()

        mocker.patch(
            "scripts.send_application_on_closure.get_fund_round",
            return_value={
                "deadline": "2022-12-01 12:00:00",
                "round_name": "COF R2W2",
            },
        )

        result = send_incomplete_applications_after_deadline(
            unique_fund_round[0], unique_fund_round[1], True
        )
        assert 1 == result, "Unexpected result number"

    @pytest.mark.apps_to_insert(
        [test_application_data[0], test_application_data[0]]
    )
    @pytest.mark.unique_fund_round(True)
    def test_send_apps_two_to_send(
        self, mocker, client, seed_application_records, unique_fund_round
    ):

        mocker.patch(
            "scripts.send_application_on_closure.get_fund_round",
            return_value={
                "deadline": "2022-12-01 12:00:00",
                "round_name": "COF R2W2",
            },
        )

        result = send_incomplete_applications_after_deadline(
            unique_fund_round[0], unique_fund_round[1], True
        )
        assert 2 == result, "Unexpected result number"

    @pytest.mark.apps_to_insert(
        [
            test_application_data[0],
            {
                "account_id": "bad_id",
                "fund_id": "47aef2f5-3fcb-4d45-acb5-f0152b5f03c4",
                "language": "en",
                "round_id": "c603d114-5364-4474-a0c4-c41cbf4d3bbd",
            },
        ]
    )
    @pytest.mark.unique_fund_round(True)
    def test_send_apps_one_to_send_one_bad_id(
        self, mocker, client, seed_application_records, unique_fund_round
    ):

        mocker.patch(
            "scripts.send_application_on_closure.get_fund_round",
            return_value={
                "deadline": "2022-12-01 12:00:00",
                "round_name": "COF R2W2",
            },
        )
        # When send emails is true we should get an exception
        with raises(LookupError):
            result = send_incomplete_applications_after_deadline(
                unique_fund_round[0], unique_fund_round[1], True
            )

        # When send emails is false it should return how many were ok to send
        result = send_incomplete_applications_after_deadline(
            unique_fund_round[0], unique_fund_round[1], False
        )
        assert 1 == result, "Unexpected result number"

    def test_send_apps_before_deadline(self, mocker, app):
        fund_id = UnitTestingConfig.COF_FUND_ID
        round_id = UnitTestingConfig.COF_ROUND_2_ID

        mocker.patch(
            "scripts.send_application_on_closure.get_fund_round",
            return_value={"deadline": "2025-01-01 12:00:00"},
        )

        result = send_incomplete_applications_after_deadline(fund_id, round_id)
        assert -1 == result, "Unexpected result number"
