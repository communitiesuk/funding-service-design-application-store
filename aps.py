from datetime import datetime

import api.routes.application.helpers
import click
from api.routes.application.helpers import get_account
from config import Config
from db.models.applications import ApplicationsMethods
from db.models.forms import FormsMethods
from external_services.models.notification import Notification
from flask import current_app

# @click.command()
# @click.option(
#     "--fund_id",
#     prompt="Enter fund_id: ",
#     help="Provide fund_id from the fund.",
# )
# @click.option(
#     "--round_id",
#     prompt="Enter round_id: ",
#     help="Provide fund_id from the fund.",
# )
def send_email_on_deadline_task(fund_id, round_id):

    current_date_time = (
        datetime.now().replace(microsecond=0).strftime("%Y-%m-%d %H:%M:%S")
    )
    fund_rounds = api.routes.application.helpers.get_data(
        Config.FUND_STORE_API_HOST
        + Config.FUND_ROUND_ENDPOINT.format(fund_id=fund_id, round_id=round_id)
    )

    if current_date_time < fund_rounds.get("deadline"):  # Change < to >
        status = {
            "status_only": "IN_PROGRESS",
            "fund_id": fund_id,
            "round_id": round_id,
        }
        in_progress_applications = ApplicationsMethods.search_applications(
            **status
        )

        all_applications = []
        for application in in_progress_applications:
            application["forms"] = FormsMethods.get_forms_by_app_id(application.get("id"))
            application["round_name"] = fund_rounds.get("title")
            
            #----------------------------------------------------------------------
            # Update submission date temporarily to test out Notification response - DELETE after testing # noqa
            application.update(
                {"date_submitted": "2022-09-21T13:37:31.032064"}
            )

            #----------------------------------------------------------------------
            
            account_store_response = get_account(account_id=application.get("account_id"))
            application['account_email'] = account_store_response.email
            all_applications.append({"application": application})
            
        if len(all_applications) > 0:
            for application in all_applications:
                email = {'email':application.get("account_email") for application in application.values()}
                Notification.send(
                    template_type=Config.NOTIFY_TEMPLATE_SUBMIT_APPLICATION,
                    to_email=email.get('email'),
                    content=application,
                )
        else:
            return "There are no applications to be sent."
    else:
        return "Current round is active"



# if __name__ == "__main__":
#     send_email_on_deadline_task()
#     # app.run(debug=True)
#     # hello()
