import json
import os
from typing import Optional

import requests
from flask import current_app

from config import Config
from external_services.exceptions import NotificationError


def post_data(endpoint: str, json_payload: Optional[dict] = None) -> dict:
    if Config.USE_LOCAL_DATA:
        current_app.logger.info("Posting to local dummy endpoint: {endpoint}", extra=dict(endpoint=endpoint))
        response = post_local_data(endpoint)

    else:
        if json_payload:
            json_payload = {k: v for k, v in json_payload.items() if v is not None}
        current_app.logger.info(
            "Attempting POST to the following endpoint: '{endpoint}'.",
            extra=dict(endpoint=endpoint),
        )
        response = requests.post(endpoint, json=json_payload)

    if response.status_code in [200, 201]:
        current_app.logger.info(
            "Post successfully sent to {endpoint} with response code: '{status_code}'.",
            extra=dict(endpoint=endpoint, status_code=response.status_code),
        )

        return response.json()

    raise NotificationError(
        message=(
            "Sorry, the notification could not be sent for endpoint:"
            f" '{endpoint}', params: '{json_payload}', response:"
            f" '{response.json()}'"
        )
    )


def post_local_data(endpoint):
    api_data_json = os.path.join(Config.FLASK_ROOT, "tests", "api_data", "post_endpoint_data.json")
    with open(api_data_json) as json_file:
        api_data = json.load(json_file)
    if endpoint in api_data:
        mocked_response = requests.models.Response()
        mocked_response.status_code = 200
        content_str = json.dumps(api_data[endpoint])
        mocked_response._content = bytes(content_str, "utf-8")
        return mocked_response
    return None
