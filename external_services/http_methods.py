import requests
from external_services.exceptions import CustomError
from flask import current_app


def post_data(endpoint: str, params: dict = None):

    if params:
        params = {k: v for k, v in params.items() if v is not None}
    current_app.logger.info(
        f"Attempting POST to the following endpoint: '{endpoint}'."
    )
    response = requests.post(endpoint, json=params)
    if response.status_code in [200, 201]:
        current_app.logger.info(
            "Post successfully sent to {endpoint} with response code:"
            f" '{response.status_code}'."
        )

        return response.json()

    raise CustomError(
        message=(
            "Sorry, the notification could not be sent for endpoint:"
            f" '{endpoint}', params: '{params}'."
        )
    )
