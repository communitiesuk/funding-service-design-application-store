import json
import os
from operator import itemgetter

import requests
from config import Config
from flask import abort
from flask import current_app
from external_services.models.fund import Fund
from typing import List

from config import Config
from external_services.models.fund import Fund
from external_services.models.round import Round
from flask import current_app


class ApplicationHelpers:
    @staticmethod
    def get_blank_forms(fund_id: str, round_id: str):
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
            fund_round_forms = Config.FUND_ROUND_FORMS
            forms = fund_round_forms.get(":".join([fund_id, round_id]))
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
        ordered_applications = []
        if order_by and order_by in [
            "id",
            "status",
            "account_id",
            "assessment_deadline",
            "started_at",
        ]:
            ordered_applications = sorted(
                applications,
                key=itemgetter(order_by),
                reverse=order_rev,
            )

        return ordered_applications


def get_data(endpoint: str):
    """
        Queries the api endpoint provided and returns a
        data response in json format.

    Args:
        endpoint (str): an API get data address

    Returns:
        data (json): data response in json format
    """

    current_app.logger.info(f"Fetching data from '{endpoint}'.")
    if Config.USE_LOCAL_DATA:
        data = get_local_data(endpoint)
    else:
        data = get_remote_data(endpoint)
    if data is None:
        current_app.logger.error(
            f"Data request failed, unable to recover: {endpoint}"
        )
        return abort(500)
    return data

def get_remote_data(endpoint):
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

def get_local_data(endpoint: str):
    api_data_json = os.path.join(
        Config.FLASK_ROOT, "tests", "api_data", "get_endpoint_data.json"
    )
    fp = open(api_data_json)
    api_data = json.load(fp)
    fp.close()
    if endpoint in api_data:
        return api_data.get(endpoint)
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
