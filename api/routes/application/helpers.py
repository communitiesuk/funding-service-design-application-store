import json
import os
from operator import itemgetter
from typing import List
from urllib.parse import urlencode

import requests
from config import Config
from external_services.models.account import Account
from external_services.models.fund import Fund
from external_services.models.round import Round
from flask import abort
from flask import current_app


def get_forms_from_form_config(form_config, fund_id, round_id, language):
    mint_form_list = set()
    forms_config = form_config.get(":".join([fund_id, round_id]))
    for form_config in forms_config:
        for form in form_config['ordered_form_names_within_section']:
            mint_form_list.add(form[language])
    return mint_form_list

class ApplicationHelpers:
    @staticmethod
    def get_blank_forms(fund_id: str, round_id: str, language: str):
        """
        Get the list of forms required to populate a blank
        application for a fund round

        Args:
            fund_id: (str) The id of the fund
            round_id: (str) The id of the fund round

        Returns:
            A list of json forms to populate the form
        """
        fund = get_fund(fund_id)
        fund_round = get_round(fund_id, round_id)
        if fund and fund_round:
            form_config = Config.FORMS_CONFIG_FOR_FUND_ROUND
            forms = get_forms_from_form_config(form_config, fund_id, round_id, language)
            if not forms:
                raise Exception(
                    f"Could not find forms for {fund_id} - {round_id}"
                )
            return forms.copy()
        raise Exception(
            f"Could not find fund round for {fund_id} - {round_id}  in fund"
            " store."
        )

    def order_applications(applications, order_by, order_rev):
        """
        Returns a list of ordered applications
        """
        if order_by and order_by in [
            "id",
            "status",
            "account_id",
            "assessment_deadline",
            "started_at",
            "last_edited",
        ]:
            applications = sorted(
                applications,
                key=itemgetter(order_by),
                reverse=int(order_rev),
            )

        return applications


def get_data(endpoint: str, params: dict = None):
    """
        Queries the api endpoint provided and returns a
        data response in json format.

    Args:
        endpoint (str): an API get data address

    Returns:
        data (json): data response in json format
    """

    if Config.USE_LOCAL_DATA:
        current_app.logger.info(f"Fetching local data from '{endpoint}'.")
        data = get_local_data(endpoint, params)
    else:
        current_app.logger.info(f"Fetching data from '{endpoint}'.")
        data = get_remote_data(endpoint, params)
    if data is None:
        current_app.logger.error(
            f"Data request failed, unable to recover: {endpoint}"
        )
        return abort(500)
    return data


def get_remote_data(endpoint, params: dict = None):
    query_string = ""
    if params:
        params = {k: v for k, v in params.items() if v is not None}
        query_string = urlencode(params)

    endpoint = endpoint + "?" + query_string

    response = requests.get(endpoint)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        current_app.logger.warn(
            "GET remote data call was unsuccessful with status code:"
            f" {response.status_code}."
        )
        return None


def get_local_data(endpoint: str, params: dict = None):
    query_string = ""
    if params:
        params = {k: v for k, v in params.items() if v is not None}
        query_string = urlencode(params)
        endpoint = endpoint + "?" + query_string
    api_data_json = os.path.join(
        Config.FLASK_ROOT, "tests", "api_data", "get_endpoint_data.json"
    )
    with open(api_data_json) as json_file:
        api_data = json.load(json_file)
    if endpoint in api_data:
        mocked_response = requests.models.Response()
        mocked_response.status_code = 200
        content_str = json.dumps(api_data[endpoint])
        mocked_response._content = bytes(content_str, "utf-8")
        return json.loads(mocked_response.text)
    return None


def get_funds() -> List[Fund] | None:
    endpoint = Config.FUND_STORE_API_HOST + Config.FUNDS_ENDPOINT
    response = get_data(endpoint)
    if response and len(response) > 0:
        funds = []
        for fund in response:
            funds.append(Fund.from_json(fund))
        return funds


def get_fund(fund_id: str) -> Fund | None:
    endpoint = Config.FUND_STORE_API_HOST + Config.FUND_ENDPOINT.format(
        fund_id=fund_id
    )
    current_app.logger.info(f"Request made to {endpoint}")
    response = get_data(endpoint)
    print(response)
    if response is None:
        current_app.logger.info("Request to fund store returned None")
    fund = Fund.from_json(response)
    return fund


def get_rounds(fund_id: str) -> Fund | List:
    endpoint = Config.FUND_STORE_API_HOST + Config.FUND_ROUNDS_ENDPOINT.format(
        fund_id=fund_id
    )
    response = get_data(endpoint)
    rounds = []
    if response and len(response) > 0:
        for round_data in response:
            rounds.append(Round.from_json(round_data))
    return rounds


def get_round(fund_id: str, round_id: str) -> Round | None:
    """
    Gets round from round store api using round_id if given.
    """
    round_endpoint = (
        Config.FUND_STORE_API_HOST
        + Config.FUND_ROUND_ENDPOINT.format(fund_id=fund_id, round_id=round_id)
    )
    round_response = get_data(round_endpoint)
    if round_response and "id" in round_response:
        return Round.from_json(round_response)


def get_account(email: str = None, account_id: str = None) -> Account | None:
    """
    Get an account from the account store using either
    an email address or account_id.

    Args:
        email (str, optional): The account email address
        Defaults to None.
        account_id (str, optional): The account id. Defaults to None.

    Raises:
        TypeError: If both an email address or account id is given,
        a TypeError is raised.

    Returns:
        Account object or None
    """
    if email is account_id is None:
        raise TypeError("Requires an email address or account_id")

    url = Config.ACCOUNT_STORE_API_HOST + Config.ACCOUNTS_ENDPOINT
    params = {"email_address": email, "account_id": account_id}
    response = get_data(url, params)

    if response and "account_id" in response:
        return Account.from_json(response)
