from typing import List

from config import Config
from external_services import http_methods
from external_services.models.fund import Fund
from external_services.models.round import Round
from flask import current_app


def get_funds() -> List[Fund] | None:
    endpoint = Config.FUND_STORE_API_HOST + Config.FUNDS_ENDPOINT
    response = http_methods.get_data(endpoint)
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
    response = http_methods.get_data(endpoint)
    if response is None:
        current_app.logger.info("Request to fund store returned None")
    fund = Fund.from_json(response)
    return fund


def get_rounds(fund_id: str) -> Fund | List:
    endpoint = Config.FUND_STORE_API_HOST + Config.FUND_ROUNDS_ENDPOINT.format(
        fund_id=fund_id
    )
    response = http_methods.get_data(endpoint)
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
    round_response = http_methods.get_data(round_endpoint)
    if round_response and "id" in round_response:
        return Round.from_json(round_response)
