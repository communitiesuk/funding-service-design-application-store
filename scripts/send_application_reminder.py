#!/usr/bin/env python3
import argparse
import sys
from datetime import datetime
from datetime import timedelta

sys.path.insert(1, ".")

import api.routes.application.helpers as helpers
from app import app
from config import Config
from db.models.applications import ApplicationsMethods
from db.models.forms import FormsMethods
from external_services.models.notification import Notification
from flask import current_app


def application_deadline_reminder(fund_id, round_id):

    current_date_time = datetime.strptime(
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S"
    )

    fund_rounds = helpers.get_data(
        Config.FUND_STORE_API_HOST
        + Config.FUND_ROUND_ENDPOINT.format(fund_id=fund_id, round_id=round_id)
    )
    get_fund_deadline = fund_rounds.get("deadline")
    fund_deadline = datetime.fromisoformat(get_fund_deadline)
    reminder_date = fund_deadline - timedelta(days=14)

    if (current_date_time > reminder_date) and (
        current_date_time < fund_deadline
    ):

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

            application["round_name"] = fund_rounds.get("title")
            account_id = helpers.get_account(
                account_id=application.get("account_id")
            )
            application["account_email"] = account_id.email
            application["deadline_date"] = get_fund_deadline
            all_applications.append({"application": application})

        if len(all_applications) > 0:
            for count, application in enumerate(all_applications):
                email = {
                    "email": application.get("account_email")
                    for application in application.values()
                }
                current_app.logger.info(
                    f"Sending application {count+1} of"
                    f" {len(all_applications)} to {email.get('email')}"
                )
                Notification.send(
                    template_type=Config.NOTIFY_TEMPLATE_APPLICATION_DEADLINE_REMINDER,
                    to_email=email.get("email"),
                    content=application,
                )
        else:
            current_app.logger.info(
                "Currently, there are no incomplete applications"
            )
    else:
        current_app.logger.info(
            "Please send reminder two weeks before the deadline date:"
            f" {fund_deadline.strftime('%Y-%m-%d')}"
        )


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
    application_deadline_reminder(fund_id=args.fund_id, round_id=args.round_id)


if __name__ == "__main__":
    with app.app_context():
        main()
