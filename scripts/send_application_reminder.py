#!/usr/bin/env python3
import argparse
import sys

sys.path.insert(1, ".")

from external_services.exceptions import NotificationError  # noqa: E402
import external_services  # noqa: E402
from app import app  # noqa: E402
from config import Config  # noqa: E402
from external_services.models.notification import Notification  # noqa: E402
from flask import current_app  # noqa: E402
from db.queries import search_applications  # noqa: E402


def application_deadline_reminder(fund_id: str, round_id: str):

    fund_round = external_services.get_data(
        Config.FUND_STORE_API_HOST
        + Config.FUND_ROUND_ENDPOINT.format(fund_id=fund_id, round_id=round_id)
    )

    fund_deadline_string = fund_round.get("deadline")

    status = {
        "status_only": ["IN_PROGRESS", "NOT_STARTED", "COMPLETED"],
        "fund_id": fund_id,
        "round_id": round_id,
    }

    not_submitted_applications = search_applications(**status)

    all_applications = []
    for application in not_submitted_applications:

        application["round_name"] = fund_round.get("title")
        account = external_services.get_account(
            account_id=application.get("account_id")
        )
        application["account_email"] = account.email
        application["deadline_date"] = fund_deadline_string
        all_applications.append({"application": application})
        # Only one email per account_email
        unique = {}
        for application in all_applications:
            unique[application["application"]["account_email"]] = application
        unique_application_email_addresses = list(unique.values())

    if len(unique_application_email_addresses) > 0:
        for count, application in enumerate(unique_application_email_addresses):

            email = {
                "email": applicant.get("account_email")
                for applicant in application.values()
            }

            current_app.logger.info(
                f"Sending application {count+1} of"
                f" {len(all_applications)} to {email.get('email')}"
            )

            try:
                Notification.send(
                    template_type=Config.NOTIFY_TEMPLATE_APPLICATION_DEADLINE_REMINDER,  # noqa: E501
                    to_email=email.get("email"),
                    content=application,
                )
            except NotificationError as e:
                current_app.logger.error(e.message)

    else:
        current_app.logger.info("Currently, there are no non-submitted applications")


def init_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fund_id", help="Provide fund id of a fund", required=True)
    parser.add_argument("--round_id", help="Provide round id of a fund", required=True)
    return parser


def main() -> None:
    parser = init_argparse()
    args = parser.parse_args()
    application_deadline_reminder(fund_id=args.fund_id, round_id=args.round_id)


if __name__ == "__main__":
    with app.app_context():
        main()
