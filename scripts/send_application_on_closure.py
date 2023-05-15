#!/usr/bin/env python3
import argparse
import sys
from datetime import datetime

from distutils.util import strtobool

sys.path.insert(1, ".")

import external_services  # noqa: E402
from app import app  # noqa: E402
from config import Config  # noqa: E402
from db.queries import search_applications  # noqa: E402
from db.queries import get_forms_by_app_id  # noqa: E402
from external_services.models.notification import Notification  # noqa: E402
from flask import current_app  # noqa: E402


def send_incomplete_applications_after_deadline(fund_id, round_id, send_emails=False):

    """
    Gets a list of unsubmitted applications, then retrieves form and user
    data for each. Once all data is retrieved, uses the notification service
    to email the account id for each application. If send_emails is false,
    does not make calls to the notification service - useful for testing.

    Behaviour on errors is different depending on the value
    of send_emails.

    If send_emails == true:
        When an error is encountered (eg. the account_id doesn't exist
        in the account store), the whole process stops and no further emails
        are sent.
    If send_emails == false:
        When an error occurs, the process continues to the next application
        but logs the error for investigation. No emails are sent.
    """

    current_date_time = (
        datetime.now().replace(microsecond=0).strftime("%Y-%m-%d %H:%M:%S")
    )

    fund_rounds = get_fund_round(fund_id, round_id)
    if current_date_time > fund_rounds.get("deadline"):
        search_params = {
            "status_only": ["NOT_STARTED", "IN_PROGRESS", "COMPLETED"],
            "fund_id": fund_id,
            "round_id": round_id,
        }
        matching_applications = search_applications(**search_params)
        applications_to_send = []
        for application in matching_applications:
            try:
                application["forms"] = get_forms_by_app_id(application.get("id"))
                application["round_name"] = fund_rounds.get("title")
                try:
                    account_id = external_services.get_account(
                        account_id=application.get("account_id")
                    )
                    application["account_email"] = account_id.email
                    applications_to_send.append({"application": application})
                except Exception:
                    handle_error(
                        "Unable to retrieve account id"
                        f" ({application.get('account_id')}) for "
                        + f"application id {application.get('id')}",
                        send_emails,
                    )
            except Exception:
                handle_error(
                    "Unable to retrieve forms for "
                    + f"application id {application.get('id')}",
                    send_emails,
                )

        current_app.logger.info(
            f"Found {len(matching_applications)} applications with matching"
            f" statuses. Retrieved all data for {len(applications_to_send)} of"
            " them."
        )
        if send_emails:
            current_app.logger.info(
                "Send emails set to true, will now send"
                f" {len(applications_to_send)} emails."
            )
            count = 0
            if len(applications_to_send) > 0:
                for application in applications_to_send:
                    count += 1
                    email = {
                        "email": application.get("account_email")
                        for application in application.values()
                    }
                    current_app.logger.info(
                        f"Sending application {count} of"
                        f" {len(applications_to_send)} to {email.get('email')}"
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
            current_app.logger.info(
                "Send emails set to false, will not send"
                f" {len(applications_to_send)} emails."
            )
            return len(applications_to_send)
    else:
        current_app.logger.info("Current round is active")
        return -1


def handle_error(msg, throw_on_error):
    current_app.logger.error(msg)
    if throw_on_error:
        raise LookupError(msg)


def get_fund_round(fund_id, round_id):
    return external_services.get_data(
        Config.FUND_STORE_API_HOST
        + Config.FUND_ROUND_ENDPOINT.format(fund_id=fund_id, round_id=round_id)
    )


def init_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fund_id", help="Provide fund id of a fund", required=True)
    parser.add_argument("--round_id", help="Provide round id of a fund", required=True)
    parser.add_argument(
        "--send_emails",
        help="Whether to actually send emails: True or False",
        required=True,
    )
    return parser


def main() -> None:
    parser = init_argparse()
    args = parser.parse_args()
    send_incomplete_applications_after_deadline(
        fund_id=args.fund_id,
        round_id=args.round_id,
        send_emails=strtobool(args.send_emails),
    )


if __name__ == "__main__":
    with app.app_context():
        main()
