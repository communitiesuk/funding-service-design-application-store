import json
import os
from datetime import datetime
from typing import List

import pytz
import requests
from config import FLASK_ROOT
from config import FUND_STORE_API_HOST
from config import ROUND_STORE_API_HOST
from external_data.models.fund import Fund
from external_data.models.round import Round

# Fund Store Endpoints
FUNDS_ENDPOINT = "/funds/"
FUND_ENDPOINT = "/funds/{fund_id}"

# Round Store Endpoints
ROUNDS_ENDPOINT = "/fund/{fund_id}"
ROUND_ENDPOINT = "/fund/{fund_id}/round/{round_id}"


def get_data(endpoint: str):
    if endpoint[:8] == "https://":
        response = requests.get(endpoint)
        if response.status_code == 200:
            data = response.json()
        else:
            return None
    else:
        data = get_local_data(endpoint)
    return data


def get_local_data(endpoint: str):
    api_data_json = os.path.join(
        FLASK_ROOT, "tests", "api_data", "endpoint_data.json"
    )
    fp = open(api_data_json)
    api_data = json.load(fp)
    fp.close()
    if endpoint in api_data:
        return api_data.get(endpoint)


def get_funds() -> List[Fund] | None:
    endpoint = FUND_STORE_API_HOST + FUNDS_ENDPOINT
    response = get_data(endpoint)
    if response and len(response) > 0:
        funds = []
        for fund in response:
            funds.append(Fund.from_json(fund))
        return funds
    return None


def get_fund(fund_id: str) -> Fund | None:
    endpoint = FUND_STORE_API_HOST + FUND_ENDPOINT.format(fund_id=fund_id)
    response = get_data(endpoint)
    if response and "fund_id" in response:
        fund = Fund.from_json(response)
        if "rounds" in response and len(response["rounds"]) > 0:
            for fund_round in response["rounds"]:
                fund.add_round(Round.from_json(fund_round))
        return fund
    return None


def get_rounds(fund_id: str) -> Fund | List:
    endpoint = ROUND_STORE_API_HOST + ROUNDS_ENDPOINT.format(fund_id=fund_id)
    response = get_data(endpoint)
    print(endpoint)
    rounds = []
    if response and len(response) > 0:
        for round_data in response:
            rounds.append(Round.from_json(round_data))
    return rounds


def get_round(
    fund_id: str, round_id: str = None, date_submitted: datetime = None
) -> Round | None:
    """
    Gets round from round store api using round_id if given.
    If no round_id is provided, attempts to find the correct round
    based on date_submitted time and open rounds for the given fund_id
    """
    fund_round = None
    if round_id:
        round_endpoint = ROUND_STORE_API_HOST + ROUND_ENDPOINT.format(
            fund_id=fund_id, round_id=round_id
        )
        round_response = get_data(round_endpoint)
        if round_response and "round_id" in round_response:
            fund_round = Round.from_json(round_response)
        if not isinstance(fund_round, Round):
            raise Exception(
                f"Round with id '{round_id}' for fund {fund_id} could not be"
                " found"
            )

    elif date_submitted:
        rounds = get_rounds(fund_id)
        if rounds:
            for listed_round in rounds:
                round_opens = pytz.utc.localize(
                    datetime.fromisoformat(listed_round.opens)
                )
                round_deadline = pytz.utc.localize(
                    datetime.fromisoformat(listed_round.deadline)
                )
                if round_opens < date_submitted < round_deadline:
                    fund_round = listed_round
        if not isinstance(fund_round, Round):
            raise Exception(
                "Active round for application submitted at"
                f" {str(date_submitted)} fund {fund_id} could not be found"
            )
    return fund_round
