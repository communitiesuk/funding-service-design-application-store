import pytest
from app import create_app
from db.queries.application import create_application
from db.queries.form import add_new_forms
from flask import Response
from tests.helpers import local_api_call

pytest_plugins = ["fsd_utils.fixtures.db_fixtures"]


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
def seed_application_records(
    request, recreate_db, app, clear_test_data, enable_preserve_test_data
):
    marker = request.node.get_closest_marker("apps_to_insert")
    if marker is None:
        apps = [
            {
                "account_id": "usera",
                "fund_id": "47aef2f5-3fcb-4d45-acb5-f0152b5f03c4",
                "round_id": "c603d114-5364-4474-a0c4-c41cbf4d3bbd",
                "language": "en",
            },
        ]
    else:
        apps = marker.args[0]
    seeded_ids = []
    for app in apps:
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
        seeded_ids.append(app)
    yield seeded_ids


def mock_get_data(endpoint, params=None):
    return local_api_call(endpoint, params, "get")


def mock_post_data(endpoint, params=None):
    return local_api_call(endpoint, params, "post")


def mock_get_random_choices(
    population, weights=None, *, cum_weights=None, k=1
):
    return "ABCDEF"


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
