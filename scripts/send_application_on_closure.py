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
from external_services.data import get_fund  # noqa: E402
from flask import current_app  # noqa: E402


def send_incomplete_applications_after_deadline(
    fund_id, round_id, single_application, send_email, application_id=None
):
    """
    Gets a list of unsubmitted applications and retrieves form and user
    data for each. Then, it uses the notification service to email the account
    ID for each application. If send_emails is set to False, no notification
    service calls will be made (useful for testing).

    Note:
    - By default, Flag send_email and single_application are both set to False.
      Just add the Flag to the cammand line, it will set the value to True automatically.
    - To enable email notifications, include the --send_email flag in the command.
    - To process a single application, include the --single_application flag in
      the command, and also provide the --application_id parameter.

    Args:
    - fund_id (str): The ID of the fund.
    - round_id (str): The ID of the funding round.
    - single_application (bool): add Flag --single_application to the command line.
    - send_email (bool): add Falg --send_email to the command line.
    - application_id (str, optional): The single application_id to be processed
      when single_application is Flagged.
    """

    current_date_time = (
        datetime.now().replace(microsecond=0).strftime("%Y-%m-%d %H:%M:%S")
    )

    fund_rounds = get_fund_round(fund_id, round_id)
    if current_date_time > fund_rounds.get("deadline"):
        fund_data = get_fund(fund_id)
        search_params = {
            "status_only": ["NOT_STARTED", "IN_PROGRESS", "COMPLETED"],
            "fund_id": fund_id,
            "round_id": round_id,
            "application_id": application_id if single_application else None,
        }
        matching_applications = search_applications(**search_params)

        applications_to_send = []
        for application in matching_applications:
            application = {**application, "fund_name": fund_data.name}
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
                        send_email,
                    )
            except Exception:
                handle_error(
                    "Unable to retrieve forms for "
                    + f"application id {application.get('id')}",
                    send_email,
                )

        current_app.logger.info(
            f"Found {len(matching_applications)} applications with matching"
            f" statuses. Retrieved all data for {len(applications_to_send)} of"
            " them."
        )
        if send_email:
            total_applications = len(applications_to_send)
            current_app.logger.info(
                "Send email set to true, will now send"
                f" {total_applications} {'emails' if total_applications > 1 else 'email'}."
            )
            if total_applications > 0:
                for count, application in enumerate(applications_to_send, start=1):
                    email = {
                        "email": application.get("account_email")
                        for application in application.values()
                    }
                    current_app.logger.info(
                        f"Sending application {count} of"
                        f" {total_applications} to {email.get('email')}"
                    )
                    application["contact_help_email"] = fund_rounds.get("contact_email")
                    Notification.send(
                        template_type=Config.NOTIFY_TEMPLATE_INCOMPLETE_APPLICATION,  # noqa
                        to_email=email.get("email"),
                        content=application,
                    )
                current_app.logger.info(
                    f"Sent {count} {'emails' if count > 1 else 'email'}"
                )
                return count
            else:
                current_app.logger.warning("There are no applications to be sent.")
                return 0
        else:
            count = len(applications_to_send)
            current_app.logger.warning(
                "Send email set to false, will not send"
                f" {count} {'emails' if count > 1 else 'email'}."
            )
            return len(applications_to_send)
    else:
        current_app.logger.warning("Current round is active")
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
        "--single_application",
        help="Whether to send just single application",
        action="store_true",
    )
    parser.add_argument(
        "--application_id",
        help="Provide application id if single_application arg is flagged",
        required="--single_application" in sys.argv,
    )
    parser.add_argument(
        "--send_email",
        help="Whether to actually send email",
        action="store_true",
    )
    return parser


def main() -> None:
    parser = init_argparse()
    args = parser.parse_args()
    send_incomplete_applications_after_deadline(
        fund_id=args.fund_id,
        round_id=args.round_id,
        single_application=args.single_application,
        application_id=args.application_id,
        send_email=args.send_email,
    )


if __name__ == "__main__":
    with app.app_context():
        main()
