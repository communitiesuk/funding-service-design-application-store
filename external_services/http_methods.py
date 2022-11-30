from typing import Dict
from typing import Optional

import requests
from external_services.exceptions import NotificationError
from flask import current_app


def post_data(endpoint: str, json_payload: Optional[dict] = None) -> Dict:

    if json_payload:
        json_payload = {k: v for k, v in json_payload.items() if v is not None}
    current_app.logger.info(
        f"Attempting POST to the following endpoint: '{endpoint}'."
    )
    response = requests.post(endpoint, json=json_payload)
    if response.status_code in [200, 201]:
        current_app.logger.info(
            f"Post successfully sent to {endpoint} with response code:"
            f" '{response.status_code}'."
        )

        return response.json()

    raise NotificationError(
        message=(
            "Sorry, the notification could not be sent for endpoint:"
            f" '{endpoint}', params: '{json_payload}', response:"
            f" '{response.json()}'"
        )
    )
