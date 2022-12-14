#!/usr/bin/env python3
import argparse
import sys
from datetime import datetime

sys.path.insert(1, ".")

import external_services  # noqa: E402
from app import app  # noqa: E402
from config import Config  # noqa: E402
from db.queries import search_applications  # noqa: E402
from db.queries import get_forms_by_app_id  # noqa: E402
from external_services.models.notification import Notification  # noqa: E402
from flask import current_app  # noqa: E402


def send_incomplete_applications_after_deadline(fund_id, round_id):

    current_date_time = (
        datetime.now().replace(microsecond=0).strftime("%Y-%m-%d %H:%M:%S")
    )

    fund_rounds = get_fund_round(fund_id, round_id)
    if current_date_time > fund_rounds.get("deadline"):
        search_params = {
            "status_only": ["NOT_STARTED", "IN_PROGRESS"],
            "fund_id": fund_id,
            "round_id": round_id,
        }
        in_progress_applications = search_applications(**search_params)
        all_applications = []
        for application in in_progress_applications:
            application["forms"] = get_forms_by_app_id(application.get("id"))
            application["round_name"] = fund_rounds.get("title")
            account_id = external_services.get_account(
                account_id=application.get("account_id")
            )
            application["account_email"] = account_id.email
            all_applications.append({"application": application})
        count = 0
        if len(all_applications) > 0:
            for application in all_applications:
                count += 1
                email = {
                    "email": application.get("account_email")
                    for application in application.values()
                }
                current_app.logger.info(
                    f"Sending application {count} of"
                    f" {len(all_applications)} to {email.get('email')}"
                )
                Notification.send(
                    template_type=Config.NOTIFY_TEMPLATE_INCOMPLETE_APPLICATION,  # noqa
                    to_email=email.get("email"),
                    content=application,
                )
            current_app.logger.info(f"Sent {count} emails")
            return count
        else:
            current_app.logger.info("There are no applications to be sent.")
            return 0
    else:
        current_app.logger.info("Current round is active")
        return -1


def get_fund_round(fund_id, round_id):
    return external_services.get_data(
        Config.FUND_STORE_API_HOST
        + Config.FUND_ROUND_ENDPOINT.format(fund_id=fund_id, round_id=round_id)
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
    send_incomplete_applications_after_deadline(
        fund_id=args.fund_id, round_id=args.round_id
    )


if __name__ == "__main__":
    with app.app_context():
        main()
