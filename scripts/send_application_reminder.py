#!/usr/bin/env python3
import sys

sys.path.insert(1, ".")

from external_services.exceptions import NotificationError  # noqa: E402
import external_services  # noqa: E402
from config import Config  # noqa: E402
from external_services.models.notification import Notification  # noqa: E402
from flask import current_app  # noqa: E402
from db.queries import search_applications  # noqa: E402

from datetime import datetime  # noqa: E402
import requests  # noqa: E402

import pytz  # noqa: E402


def application_deadline_reminder(flask_app):
    with flask_app.app_context():
        funds = external_services.get_data(
            Config.FUND_STORE_API_HOST + Config.FUNDS_ENDPOINT
        )

        for fund in funds:
            fund_id = fund.get("id")
            round_info = external_services.get_data(
                Config.FUND_STORE_API_HOST
                + Config.FUND_ROUNDS_ENDPOINT.format(fund_id=fund_id)
            )

            uk_timezone = pytz.timezone("Europe/London")
            current_datetime = datetime.now(uk_timezone).replace(tzinfo=None)
            for round in round_info:
                round_deadline_str = round.get("deadline")
                reminder_date_str = round.get("reminder_date")

                if not reminder_date_str:
                    continue

                application_reminder_sent = round.get("application_reminder_sent")

                # Convert the string dates to datetime objects
                round_deadline = datetime.strptime(
                    round_deadline_str, "%Y-%m-%dT%H:%M:%S"
                )
                reminder_date = datetime.strptime(
                    reminder_date_str, "%Y-%m-%dT%H:%M:%S"
                )

                if (
                    not application_reminder_sent
                    and reminder_date < current_datetime < round_deadline
                ):
                    round_id = round.get("id")
                    fund_id = round.get("fumd_id")
                    round_name = round.get("title")
                    status = {
                        "status_only": ["IN_PROGRESS", "NOT_STARTED", "COMPLETED"],
                        "fund_id": fund_id,
                        "round_id": round_id,
                    }

                    not_submitted_applications = search_applications(**status)

                    all_applications = []
                    unique = {}
                    for application in not_submitted_applications:
                        application["round_name"] = round_name
                        account = external_services.get_account(
                            account_id=application.get("account_id")
                        )
                        application["account_email"] = account.email
                        application["deadline_date"] = "2024-01-31T11:59:00"
                        all_applications.append({"application": application})
                        # Only one email per account_email

                        for application in all_applications:
                            unique[
                                application["application"]["account_email"]
                            ] = application
                    unique_application_email_addresses = list(unique.values())

                    if len(unique_application_email_addresses) > 0:
                        for count, application in enumerate(
                            unique_application_email_addresses
                        ):
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

                                application_reminder_endpoint = (
                                    Config.FUND_STORE_API_HOST
                                    + Config.FUND_ROUND_APPLICATION_REMINDER_STATUS.format(
                                        round_id=round_id
                                    )
                                )
                                response = requests.put(application_reminder_endpoint)
                                if response.status_code == 200:
                                    current_app.logger.info(
                                        "The application reminder has been"
                                        f" sent successfully for round_id {round_id}"
                                    )
                            except NotificationError as e:
                                current_app.logger.error(e.message)

                    else:
                        current_app.logger.info(
                            "Currently, there are no non-submitted applications"
                        )
                else:
                    continue


if __name__ == "__main__":
    application_deadline_reminder()
