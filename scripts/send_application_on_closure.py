#!/usr/bin/env python3
import argparse
import sys
from datetime import datetime

sys.path.insert(1, ".")

import api.routes.application.helpers as helpers
from app import app
from config import Config
from db.models.applications import ApplicationsMethods
from db.models.forms import FormsMethods
from external_services.models.notification import Notification
from flask import current_app


def send_incomplete_applications_after_deadline(fund_id, round_id):

    current_date_time = (
        datetime.now().replace(microsecond=0).strftime("%Y-%m-%d %H:%M:%S")
    )

    fund_rounds = helpers.get_data(
        Config.FUND_STORE_API_HOST
        + Config.FUND_ROUND_ENDPOINT.format(fund_id=fund_id, round_id=round_id)
    )
    if current_date_time > fund_rounds.get("deadline"):
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
            application["forms"] = FormsMethods.get_forms_by_app_id(
                application.get("id")
            )
            application["round_name"] = fund_rounds.get("title")

            # Update submission date temporarily to test out Notification response - DELETE after testing # noqa
            application.update(
                {"date_submitted": "2022-09-21T13:37:31.032064"}
            )
            account_id = helpers.get_account(
                account_id=application.get("account_id")
            )
            application["account_email"] = account_id.email
            all_applications.append({"application": application})
        count = 1
        if len(all_applications) > 0:
            for application in all_applications:
                email = {
                    "email": application.get("account_email")
                    for application in application.values()
                }
                current_app.logger.info(
                    f"Sending application {count} of"
                    f" {len(all_applications)} to {email.get('email')}"
                )

                # TODO: Add new template in Govuk-notify & in Notification service
                Notification.send(
                    template_type=Config.NOTIFY_TEMPLATE_SUBMIT_APPLICATION,
                    to_email=email.get("email"),
                    content=application,
                )
                count += 1

        else:
            current_app.logger.info("There are no applications to be sent.")
    else:
        current_app.logger.info("Current round is active")


def init_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--fund_id", help="Provide fund id of a fund", required=True
    )
    parser.add_argument(
        "--round_id", help="Provide round id of a fund", required=True
    )
    return parser


def main() -> None:
    parser = init_argparse()
    args = parser.parse_args()
    send_incomplete_applications_after_deadline(
        fund_id=args.fund_id, round_id=args.round_id
    )


if __name__ == "__main__":
    with app.app_context():
        main()
