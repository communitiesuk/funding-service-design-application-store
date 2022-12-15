import copy

from config.envs.unit_testing import UnitTestingConfig
from pytest import raises
from scripts.send_application_on_closure import (
    send_incomplete_applications_after_deadline,
)  # noqa
from tests.helpers import post_data
from tests.helpers import put_data


class TestSendAppOnClosure:
    def test_send_apps_bad_account_id(self, mocker, client):
        fund_id = UnitTestingConfig.COF_FUND_ID
        round_id = UnitTestingConfig.COF_ROUND_2_ID
        app_data_bad_account = copy.copy(vanilla_application_data)
        app_data_bad_account["account_id"] = "bad_id"
        post_data(
            client,
            "/applications",
            app_data_bad_account,
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
            with raises(LookupError):
                send_incomplete_applications_after_deadline(
                    fund_id, round_id, True
                )

            result = send_incomplete_applications_after_deadline(
                fund_id, round_id, False
            )
            assert result == 0, "Not expecting result if emails not to be sent"

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
                fund_id, round_id, True
            )
            assert 0 == result, "Unexpected result number"

    def test_send_apps_send_emails_is_false(self, mocker):
        fund_id = UnitTestingConfig.COF_FUND_ID
        round_id = UnitTestingConfig.COF_ROUND_2_ID

        with (
            mocker.patch(
                "scripts.send_application_on_closure.get_fund_round",
                return_value={"deadline": "2022-01-01 12:00:00"},
            )
        ):

            result = send_incomplete_applications_after_deadline(
                fund_id, round_id, False
            )
            assert 0 == result, "Unexpected result"

    def test_send_apps_one_to_send_not_started(self, mocker, client):
        fund_id = UnitTestingConfig.COF_FUND_ID
        round_id = UnitTestingConfig.COF_ROUND_2_ID
        post_data(
            client,
            "/applications",
            vanilla_application_data,
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
                fund_id, round_id, True
            )
            assert 1 == result, "Unexpected result number"

    def test_send_apps_one_to_send_in_progress(self, mocker, client):
        fund_id = UnitTestingConfig.COF_FUND_ID
        round_id = UnitTestingConfig.COF_ROUND_2_ID
        response = post_data(
            client,
            "/applications",
            vanilla_application_data,
        )

        put_data(
            client,
            "/applications/forms",
            {
                "metadata": {
                    "form_name": "project-information",
                    "application_id": response.json["id"],
                    "is_summary_page_submit": True,
                },
                "questions": form_data_project_info,
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
                fund_id, round_id, True
            )
            assert 1 == result, "Unexpected result number"

    def test_send_apps_two_to_send(self, mocker, client):
        fund_id = UnitTestingConfig.COF_FUND_ID
        round_id = UnitTestingConfig.COF_ROUND_2_ID
        # Add one not_started application
        response = post_data(
            client,
            "/applications",
            vanilla_application_data,
        )
        # add one in_progress application
        response = post_data(
            client,
            "/applications",
            vanilla_application_data,
        )

        put_data(
            client,
            "/applications/forms",
            {
                "metadata": {
                    "form_name": "project-information",
                    "application_id": response.json["id"],
                    "is_summary_page_submit": True,
                },
                "questions": form_data_project_info,
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
                fund_id, round_id, True
            )
            assert 2 == result, "Unexpected result number"

    def test_send_apps_one_to_send_one_bad_id(self, mocker, client):
        fund_id = UnitTestingConfig.COF_FUND_ID
        round_id = UnitTestingConfig.COF_ROUND_2_ID
        # Add one not_started application
        post_data(
            client,
            "/applications",
            vanilla_application_data,
        )
        app_data_bad_account = copy.copy(vanilla_application_data)
        app_data_bad_account["account_id"] = "bad_id"
        # add one application with bad id
        post_data(
            client,
            "/applications",
            app_data_bad_account,
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
            with raises(LookupError):
                result = send_incomplete_applications_after_deadline(
                    fund_id, round_id, True
                )

            result = send_incomplete_applications_after_deadline(
                fund_id, round_id, False
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


vanilla_application_data = {
    "account_id": "usera",
    "date_submitted": "null",
    "fund_id": "47aef2f5-3fcb-4d45-acb5-f0152b5f03c4",
    "language": "en",
    "project_name": "unsubmitted project 1",
    "reference": "COF-R2W2-LYDANK",
    "round_id": "c603d114-5364-4474-a0c4-c41cbf4d3bbd",
}

form_data_project_info = [
    {
        "fields": [
            {
                "answer": False,
                "key": "gScdbf",
                "title": (
                    "Have you been given funding through the"
                    " Community Ownership Fund before?"
                ),
                "type": "list",
            }
        ],
        "question": "About your project",
        "status": "COMPLETED",
    },
    {
        "fields": [
            {
                "answer": "unsubmitted project 1",
                "key": "KAgrBz",
                "title": "Project name",
                "type": "text",
            },
            {
                "answer": "asdfasdf",
                "key": "wudRxx",
                "title": (
                    "Tell us how the asset is currently being"
                    " used, or how it has been used before,"
                    " and why it's important to the community"
                ),
                "type": "text",
            },
            {
                "answer": "asdfadsfa",
                "key": "TlGjXb",
                "title": (
                    "Explain why the asset is at risk of being"
                    " lost to the community, or why it has"
                    " already been lost"
                ),
                "type": "text",
            },
            {
                "answer": "sdfasdf",
                "key": "GCjCse",
                "title": (
                    "Give a brief summary of your project,"
                    " including what you hope to achieve"
                ),
                "type": "text",
            },
        ],
        "question": "About your project",
        "status": "COMPLETED",
    },
    {
        "fields": [
            {
                "answer": "asdf, asdf, asdf, null, PL1 3RE",
                "key": "yEmHpp",
                "title": "Address of the community asset",
                "type": "text",
            },
            {
                "answer": "asdfasdf",
                "key": "iTeLGU",
                "title": "In which constituency is your asset?",
                "type": "text",
            },
            {
                "answer": "adsfadsfafsdfasd",
                "key": "MGRlEi",
                "title": "In which local council area is your asset?",
                "type": "text",
            },
        ],
        "question": "About your project",
        "status": "COMPLETED",
    },
]
