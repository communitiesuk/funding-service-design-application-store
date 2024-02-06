import sys

import click

sys.path.insert(1, ".")

from app import app  # noqa: E402
from db.models.application.applications import Status  # noqa: E402
from fsd_test_utils.test_config.useful_config import UsefulConfig  # noqa: E402
from tests.seed_data.seed_db import seed_in_progress_application  # noqa: E402
from tests.seed_data.seed_db import (  # noqa: E402
    seed_not_started_application,
    seed_completed_application,
    seed_submitted_application,
)  # noqa: E402


FUND_CONFIG = {
    "COF": {
        "id": UsefulConfig.COF_FUND_ID,
        "short_code": "COF",
        "rounds": {
            "R3W1": {
                "short_code": "R3W1",
                "id": UsefulConfig.COF_ROUND_3_W1_ID,
                "project_name_form": "project-information-cof-r3-w1",
            },
            "R3W2": {
                "short_code": "R3W2",
                "id": UsefulConfig.COF_ROUND_3_W2_ID,
                "project_name_form": "project-information-cof-r3-w2",
            },
        },
    },
    "NSTF": {
        "id": UsefulConfig.NSTF_FUND_ID,
        "short_code": "NSTF",
        "rounds": {
            "R2": {
                "short_code": "R2",
                "id": UsefulConfig.NSTF_ROUND_2_ID,
                "project_name_form": "name-your-application-ns",
            }
        },
    },
}


@click.command()
@click.option(
    "--fund_short_code",
    default="COF",
    type=click.Choice(["COF", "NSTF"]),
    help="Fund to seed applications for",
    prompt=True,
)
@click.option(
    "--round_short_code",
    default="R3W2",
    type=click.Choice(["R3W2", "R3W1", "R2"]),
    help="Round to seed applications for",
    prompt=True,
)
@click.option(
    "--account_id",
    default="7d00296f-6dd6-47fe-a084-48d94fecf3fa",
    help="Account ID to seed applications for",
    prompt=True,
)
@click.option(
    "--status",
    default="IN_PROGRESS",
    type=click.Choice(["NOT_STARTED", "IN_PROGRESS", "COMPLETED", "SUBMITTED"]),
    help="Target status for seeded applications",
    prompt=True,
)
@click.option("--count", default=1, help="Number of applications to create", prompt=True)
def seed_applications(fund_short_code, round_short_code, account_id, status, count):
    language = "en"

    fund_config = FUND_CONFIG[fund_short_code]
    round_config = fund_config["rounds"][round_short_code]
    match status:
        case Status.NOT_STARTED.name:
            for i in range(count):
                app = seed_not_started_application(
                    fund_config=fund_config,
                    round_config=round_config,
                    account_id=account_id,
                    language=language,
                )
                print(f"{app.id} - {app.reference} - {app.status.name}")
        case Status.IN_PROGRESS.name:
            for i in range(count):
                app = seed_in_progress_application(
                    fund_config=fund_config,
                    round_config=round_config,
                    account_id=account_id,
                    language=language,
                )
                print(f"{app.id} - {app.reference} - {app.status.name}")
        case Status.COMPLETED.name:
            for i in range(count):
                app = seed_completed_application(
                    fund_config=fund_config,
                    round_config=round_config,
                    account_id=account_id,
                    language=language,
                )
                print(f"{app.id} - {app.reference} - {app.status.name}")
        case Status.SUBMITTED.name:
            for i in range(count):
                app = seed_submitted_application(
                    fund_config=fund_config,
                    round_config=round_config,
                    account_id=account_id,
                    language=language,
                )
                print(f"{app.id} - {app.reference} - {app.status.name}")
        case _:
            print(f"Status {status} is not supported")
            exit(-1)


if __name__ == "__main__":
    with app.app_context():
        seed_applications()
