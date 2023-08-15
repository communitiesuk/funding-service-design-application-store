from app import app  # noqa: E402
from db.models.application.applications import Status
from fsd_test_utils.test_config.useful_config import UsefulConfig
from tests.seed_data.seed_db import seed_in_progress_application
from tests.seed_data.seed_db import seed_not_started_application


def seed_applications():
    account_id = "00000000-0000-0000-0000-000000000000"
    fund_id = ""
    round_id = ""
    language = "en"

    print("Available funds/rounds:")
    print(f"\tCOF:\t{UsefulConfig.COF_FUND_ID}")
    print(f"\t\tR3W1:\t{UsefulConfig.COF_ROUND_3_W1_ID}")

    fund_id = input("Enter fund ID: ")
    round_id = input("Enter round ID: ")
    account_id = input("Enter account ID: ")
    num_to_create = int(input("Enter number of applications to create: "))
    desired_status = input("Enter desired status: ")

    match desired_status:
        case Status.NOT_STARTED.name:
            for i in range(num_to_create):
                app = seed_not_started_application(
                    fund_id=fund_id,
                    round_id=round_id,
                    account_id=account_id,
                    language=language,
                )
                print(f"{app.id} - {app.reference} - {app.status.name}")
        case Status.IN_PROGRESS.name:
            for i in range(num_to_create):
                app = seed_in_progress_application(
                    fund_id=fund_id,
                    round_id=round_id,
                    account_id=account_id,
                    language=language,
                )
                print(f"{app.id} - {app.reference} - {app.status.name}")
        case _:
            print(f"Status {desired_status} is not supported")
            exit(-1)


def main() -> None:
    # parser = init_argparse()
    # args = parser.parse_args()
    seed_applications()


if __name__ == "__main__":
    with app.app_context():
        main()
