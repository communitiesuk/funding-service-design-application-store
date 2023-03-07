from datetime import datetime
from uuid import uuid4

import pytest
from app import create_app
from db import db
from db.queries.application import create_application
from db.queries.form import add_new_forms
from external_services.models.fund import Fund
from external_services.models.fund import Round
from flask import Response
from flask_migrate import upgrade
from tests.helpers import local_api_call
from tests.helpers import test_application_data
from tests.helpers import test_question_data

# Make the utils fixtures available, used in seed_application_records
pytest_plugins = ["fsd_utils.fixtures.db_fixtures"]

# from sqlalchemy.orm import scoped_session
# from sqlalchemy.orm import sessionmaker


@pytest.fixture(scope="session")
def app():
    """
    Creates the test client we will be using to test the responses
    from our app, this is a test fixture.
    :return: A flask test client.
    """
    app = create_app()
    yield app


@pytest.fixture(scope="function")
def unique_fund_round(mock_get_fund, mock_get_round):
    """
    Returns a tuple of 2 random uuids as fund_id and round_id.
    Requests mock_get_fund and mock_get_round so when the app
    looks up fund/round data it matches with these.
    """
    return (str(uuid4()), str(uuid4()))


@pytest.fixture(scope="function")
def seed_application_records(
    request,
    app,
    clear_test_data,
    enable_preserve_test_data,
    unique_fund_round,
):
    """
    Inserts application data on a per-test (function scoped) basis
    to prevent test pollution. Provides the inserted records to tests
    so they can access them.

    Each inserted application has 3 blank forms attached (declarations,
    project-info, org-info, or their welsh equivalents depending
    on language).
    """
    marker = request.node.get_closest_marker("apps_to_insert")
    if marker is None:
        apps = [test_application_data[0]]
    else:
        apps = marker.args[0]
    unique_fr_marker = request.node.get_closest_marker("unique_fund_round")

    seeded_apps = []
    for app in apps:
        if unique_fr_marker is not None:
            app["fund_id"] = unique_fund_round[0]
            app["round_id"] = unique_fund_round[1]
        app = create_application(**app)
        add_new_forms(
            [
                "datganiadau"
                if (app.language and app.language.name == "cy")
                else "declarations"
            ],
            app.id,
        )
        add_new_forms(
            [
                "gwybodaeth-am-y-prosiect"
                if (app.language and app.language.name == "cy")
                else "project-information"
            ],
            app.id,
        )
        add_new_forms(
            [
                "gwybodaeth-am-y-sefydliad"
                if (app.language and app.language.name == "cy")
                else "organisation-information"
            ],
            app.id,
        )
        seeded_apps.append(app)
    yield seeded_apps


@pytest.fixture(scope="function")
def add_org_data_for_reports(seed_application_records, client):
    """
    Adds additional form data to the application so it is present for
    testing the reports. Uses seed_application_records to update
    all the applications that were inserted. Each org name is unique
    in the format 'Test Org Name {n}' where n is the index+1 of the
    application's position in seed_application_records.
    """
    i = 0
    for application in seed_application_records:
        i += 1
        sections_put_en = [
            {
                "questions": test_question_data,
                "metadata": {
                    "application_id": application.id,
                    "form_name": "organisation-information",
                    "is_summary_page_submit": False,
                },
            },
            {
                "questions": [
                    {
                        "question": "Address",
                        "fields": [
                            {
                                "key": "yEmHpp",
                                "title": "Address",
                                "type": "text",
                                "answer": "BBC, W1A 1AA",
                            },
                        ],
                    },
                ],
                "metadata": {
                    "application_id": application.id,
                    "form_name": "project-information",
                    "is_summary_page_submit": False,
                },
            },
        ]
        # Make the org names unique
        sections_put_en[0]["questions"][1]["fields"][0][
            "answer"
        ] = f"Test Org Name {i}"

        for section in sections_put_en:
            client.put(
                "/applications/forms",
                json=section,
                follow_redirects=True,
            )


def mock_get_data(endpoint, params=None):
    return local_api_call(endpoint, params, "get")


def mock_post_data(endpoint, params=None):
    return local_api_call(endpoint, params, "post")


def mock_get_random_choices(
    population, weights=None, *, cum_weights=None, k=1
):
    return "ABCDEF"


def generate_mock_fund(fund_id: str) -> Fund:
    return Fund("Generated test fund", fund_id, "TEST", "Testing fund", [])


@pytest.fixture(scope="function", autouse=True)
def mock_get_fund(mocker):
    """
    Generates a mock fund with the supplied fund ID.
    Used with unique_fund_round to ensure when the fund and
    round are retrieved, they match what's expected
    """
    mocker.patch(
        "db.queries.application.queries.get_fund", new=generate_mock_fund
    )


def generate_mock_round(fund_id: str, round_id: str) -> Round:
    return Round(
        "Generated test round",
        round_id,
        fund_id,
        "TEST",
        datetime.strptime("2023-01-01 12:00:00", "%Y-%m-%d %H:%M:%S"),
        datetime.strptime("2023-01-31 12:00:00", "%Y-%m-%d %H:%M:%S"),
        datetime.strptime("2023-03-31 12:00:00", "%Y-%m-%d %H:%M:%S"),
        [],
    )


@pytest.fixture(scope="function", autouse=True)
def mock_get_round(mocker):
    """
    Generates a mock round with the supplied fund and round IDs
    Used with unique_fund_round to ensure when the fund and
    round are retrieved, they match what's expected
    """
    mocker.patch(
        "db.queries.application.queries.get_round", new=generate_mock_round
    )
    mocker.patch(
        "db.schemas.application.get_round_name",
        return_value="Generated test round",
    )


@pytest.fixture(autouse=True)
def mock_get_data_fix(mocker):
    # mock the function in the file it is invoked (not where it is declared)
    mocker.patch(
        "external_services.get_data",
        new=mock_get_data,
    )


@pytest.fixture()
def mock_random_choices(mocker):
    # mock the function in the file it is invoked (not where it is declared)
    mocker.patch("random.choices", new=mock_get_random_choices)


@pytest.fixture()
def mock_successful_submit_notification(mocker):
    # mock the function in the file it is invoked (not where it is declared)
    mocker.patch(
        "api.routes.application.routes.Notification.send",
        lambda template, email, application: Response(200),
    )


@pytest.fixture(autouse=True)
def mock_post_data_fix(mocker):
    # mock the function in the file it is invoked (not where it is declared)
    mocker.patch(
        "external_services.post_data",
        new=mock_post_data,
    )


@pytest.fixture(scope="session")
def _db(app):
    """
    Provide the transactional fixtures with access
    to the database via a Flask-SQLAlchemy
    database connection.
    """
    return db


@pytest.fixture(autouse=True)
def clear_database(_db):
    """
    Fixture to clean up the database after each test.

    This fixture clears the database by deleting all data
    from tables and disabling foreign key checks before the test,
    and resetting foreign key checks after the test.

    Args:
    _db: The database instance.
    """
    yield

    # disable foreign key checks
    _db.session.execute("SET session_replication_role = replica")
    # delete all data from tables
    for table in reversed(db.metadata.sorted_tables):
        _db.session.execute(table.delete())
    # reset foreign key checks
    _db.session.execute("SET session_replication_role = DEFAULT")
    _db.session.commit()
