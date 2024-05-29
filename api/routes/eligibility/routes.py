from config import Config
from flask import current_app
from flask import request
from flask.views import MethodView


def mock_determine_eligibility(json):
    # TODO replace this with a real call to the decision api as per
    # https://github.com/communitiesuk/funding-service-design-application-store/blob/main/api/routes/application/routes.py#L331  # noqa
    return not (json["questions"][0]["fields"][0]["answer"] == "Nope")


class EligibilityView(MethodView):
    def put(self):
        json = request.get_json()
        is_eligible = mock_determine_eligibility(json)
        current_app.logger.info(f"Received PUT for eligibility, response is {is_eligible}")
        json["metadata"]["is_eligible"] = is_eligible
        if not is_eligible:
            json["metadata"]["not_eligible_redirect_url"] = (
                Config.ELIGIBILITY_RESULT_REDIRECT_URL + f"?result={is_eligible}"
            )
        return json, 200
