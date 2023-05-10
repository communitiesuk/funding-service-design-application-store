import functools
import json
import os
from typing import List
from typing import Optional
from urllib.parse import urlencode

import requests
from config import Config
from flask import abort
from flask import current_app

from .models.account import Account
from .models.fund import Fund
from .models.round import Round


def get_data(endpoint: str, params: Optional[dict] = None):
    """
        Queries the api endpoint provided and returns a
        data response in json format.

    Args:
        endpoint (str): an API get data address

    Returns:
        data (json): data response in json format
    """

    if Config.USE_LOCAL_DATA:
        current_app.logger.info(
            f"Fetching local data from '{endpoint}'" + f" with params {params}."
        )
        data = get_local_data(endpoint, params)
    else:
        current_app.logger.info(
            f"Fetching data from '{endpoint}'" + f" with params {params}."
        )
        data = get_remote_data(endpoint, params)
    if data is None:
        current_app.logger.error(f"Data request failed, unable to recover: {endpoint}")
        return abort(500)
    return data


def get_remote_data(endpoint, params: Optional[dict] = None):
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


def get_local_data(endpoint: str, params: Optional[dict] = None):
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
    endpoint = Config.FUND_STORE_API_HOST + Config.FUND_ENDPOINT.format(fund_id=fund_id)
    current_app.logger.info(f"Request made to {endpoint}")
    response = get_data(endpoint)
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
    round_endpoint = Config.FUND_STORE_API_HOST + Config.FUND_ROUND_ENDPOINT.format(
        fund_id=fund_id, round_id=round_id
    )
    round_response = get_data(round_endpoint)
    if round_response and "id" in round_response:
        return Round.from_json(round_response)


def get_account(
    email: Optional[str] = None, account_id: Optional[str] = None
) -> Account | None:
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


@functools.lru_cache(maxsize=1)
def get_round_name(fund_id, round_id):
    response = get_data(
        Config.FUND_STORE_API_HOST
        + Config.FUND_ROUND_ENDPOINT.format(fund_id=fund_id, round_id=round_id)
    )
    if response:
        return response.get("title")
