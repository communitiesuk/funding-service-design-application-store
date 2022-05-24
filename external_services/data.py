import json
import os
import urllib.parse
from typing import List

import requests
from config import FLASK_ROOT
from config import FUND_ENDPOINT
from config import FUND_STORE_API_HOST
from config import FUNDS_ENDPOINT
from config import ROUND_ENDPOINT
from config import ROUND_STORE_API_HOST
from config import ROUNDS_ENDPOINT
from external_services.models.fund import Fund
from external_services.models.round import Round


def api_call(endpoint: str, method: str = "GET", params: dict = None):
    if params:
        params = {k: v for k, v in params.items() if v is not None}
    if endpoint[:4] == "http":
        if method:
            if method == "POST":
                return requests.post(endpoint, json=params)
            elif method == "GET":
                req = requests.PreparedRequest()
                req.prepare_url(endpoint, params)
                return requests.get(req.url)
    else:
        return local_api_call(endpoint, params, method)


def get_data(endpoint: str, params: dict = None):
    if params:
        params = {k: v for k, v in params.items() if v is not None}
    if endpoint[:4] == "http":
        req = requests.PreparedRequest()
        req.prepare_url(endpoint, params)
        response = requests.get(req.url)
        if response.status_code == 200:
            return response.json()
    else:
        return local_api_call(endpoint, params, "get")


def post_data(endpoint: str, params: dict = None):
    if params:
        params = {k: v for k, v in params.items() if v is not None}
    if endpoint[:4] == "http":
        response = requests.post(endpoint, json=params)
        if response.status_code in [200, 201]:
            return response.json()
    else:
        return local_api_call(endpoint, params, "post")


def local_api_call(endpoint: str, params: dict = None, method: str = "get"):
    api_data_json = os.path.join(
        FLASK_ROOT,
        "tests",
        "api_data",
        method.lower() + "_endpoint_data.json",
    )
    fp = open(api_data_json)
    api_data = json.load(fp)
    fp.close()
    query_params = "_"
    if params:
        query_params = urllib.parse.urlencode(params)
    if method.lower() == "post":
        if endpoint in api_data:
            post_dict = api_data.get(endpoint)
            if query_params in post_dict:
                return post_dict.get(query_params)
            else:
                return post_dict.get("_default")
    else:
        if params:
            endpoint = f"{endpoint}?{query_params}"
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


def get_fund(fund_id: str) -> Fund | None:
    endpoint = FUND_STORE_API_HOST + FUND_ENDPOINT.format(fund_id=fund_id)
    response = get_data(endpoint)
    print(endpoint)
    print(response)
    if response and "fund_id" in response:
        fund = Fund.from_json(response)
        if "rounds" in response and len(response["rounds"]) > 0:
            for fund_round in response["rounds"]:
                fund.add_round(Round.from_json(fund_round))
        return fund


def get_rounds(fund_id: str) -> Fund | List:
    endpoint = ROUND_STORE_API_HOST + ROUNDS_ENDPOINT.format(fund_id=fund_id)
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
    round_endpoint = ROUND_STORE_API_HOST + ROUND_ENDPOINT.format(
        fund_id=fund_id, round_id=round_id
    )
    round_response = get_data(round_endpoint)
    print(round_endpoint)
    print(round_response)
    if round_response and "round_id" in round_response:
        return Round.from_json(round_response)
