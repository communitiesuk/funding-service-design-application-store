import os
import venv
from pathlib import Path

from colored import attr, fg, stylize
from invoke import task

ECHO_STYLE = fg("light_gray") + attr("bold")


@task
def virtualenv(c):
    if not os.getenv("VIRTUAL_ENV") and not Path(".venv").exists():
        print(stylize("creating virtualenv at `.venv`", ECHO_STYLE))
        venv.create("venv", with_pip=True)

    c.virtual_env = Path(os.getenv("VIRTUAL_ENV", ".venv"))

    venv_path = c.virtual_env.resolve() / "bin"
    if not os.environ["PATH"].startswith(str(venv_path)):
        print(stylize(f"entering virtualenv at `{c.virtual_env}`", ECHO_STYLE))
        os.environ["PATH"] = f"{venv_path}:{os.getenv('PATH')}"

    else:
        print(stylize(f"In virtualenv at `{c.virtual_env}`", ECHO_STYLE))

    # skip if dry run
    if not c.config["run"].get("dry"):
        # we want to be sure that we are going to use python/pip from the venv
        which_python = Path(c.run("which python", hide=True).stdout.strip())
        expected_python = c.virtual_env / "bin" / "python"
        assert which_python.samefile(
            expected_python
        ), f"expected `which python` to return {expected_python}, instead got {which_python}\nPATH={os.environ['PATH']}"


@task
def bootstrap_test_db(c, database_host="localhost"):
    """Create a clean database for testing"""
    c.run(f"dropdb -h {database_host} --if-exists fsd_app_store_test")
    print(
        stylize(
            f"fsd_app_store_test db dropped from {database_host}...",
            ECHO_STYLE,
        )
    )
    c.run(f"createdb -h {database_host} fsd_app_store_test")
    print(stylize(f"fsd_app_store_test db created on {database_host}...", ECHO_STYLE))


# @task
# def seed_applications(c, database_host="localhost"):
#     from flask import current_app

#     account_id = "00000000-0000-0000-0000-000000000000"
#     fund_id = ""
#     round_id = ""
#     language = "en"

#     print("Available funds/rounds:")
#     print(f"\tCOF:\t{UsefulConfig.COF_FUND_ID}")
#     print(f"\t\tR2W1:\t{UsefulConfig.COF_ROUND_3_W1_ID}")

#     fund_id = input("Enter fund ID: ")
#     round_id = input("Enter round ID: ")

#     app = seed_not_started_application(fund_id=fund_id, round_id=round_id, account_id=account_id, language=language)
#     print(f"{app.id} - {app.reference} - {app.status}")
