import requests
from flask import current_app


def get_data(endpoint: str, params: dict = None):
    if params:
        params = {k: v for k, v in params.items() if v is not None}
    req = requests.PreparedRequest()
    req.prepare_url(endpoint, params)
    current_app.logger.info(f"HTTP request made to {endpoint}")
    response = requests.get(req.url)
    if response.status_code == 200:
        return response.json()


def post_data(endpoint: str, params: dict = None):
    if params:
        params = {k: v for k, v in params.items() if v is not None}
    response = requests.post(endpoint, json=params)
    if response.status_code in [200, 201]:
        return response.json()
