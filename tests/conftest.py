from datetime import datetime
from uuid import uuid4

import pytest
from app import create_app
from db.models.application.applications import Applications
from db.queries.application import create_application
from db.queries.form import add_new_forms
from external_services.models.fund import Fund
from external_services.models.fund import Round
from flask import Response
from tests.helpers import APPLICATION_DISPLAY_CONFIG
from tests.helpers import local_api_call
from tests.helpers import test_application_data
from tests.helpers import test_question_data
from tests.helpers import test_question_data_cy

# Make the utils fixtures available, used in seed_application_records
pytest_plugins = ["fsd_test_utils.fixtures.db_fixtures"]


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


def get_args(seed_application_records, unique_fund_round, single_app):
    application_ids = [str(application).split()[-1][:-1] for application in seed_application_records]
    args = {
        "fund_id": unique_fund_round[0],
        "round_id": unique_fund_round[1],
        "single_application": True,
        "application_id": application_ids[0] if single_app else None,
        "send_email": False,
    }
    return args


def create_app_with_blank_forms(app_to_create: dict) -> Applications:
    """
    Creates a new application record in the database using the supplied
    dictionary of application fields.
    Each inserted application has 3 blank forms attached (declarations,
    project-info, org-info, or their welsh equivalents depending
    on language).
    """
    app = create_application(**app_to_create)
    add_new_forms(
        ["datganiadau" if (app.language and app.language.name == "cy") else "declarations"],
        app.id,
    )
    add_new_forms(
        ["gwybodaeth-am-y-prosiect" if (app.language and app.language.name == "cy") else "project-information"],
        app.id,
    )
    add_new_forms(
        ["gwybodaeth-am-y-sefydliad" if (app.language and app.language.name == "cy") else "organisation-information"],
        app.id,
    )
    return app


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
        created_app = create_app_with_blank_forms(app)
        seeded_apps.append(created_app)
    yield seeded_apps


def add_org_data_for_reports(application, unique_append, client):
    """
    Adds additional form data to the application so it is present for
    testing the reports. Each org name is unique
    in the format 'Test Org Name {unique_append}'
    """
    if application.language and application.language.name == "cy":
        form_names = ["gwybodaeth-am-y-sefydliad", "gwybodaeth-am-y-prosiect"]
        address = "WelshGov, CF10 3NQ"
        unique_append = str(unique_append) + "cy"
        question_data = test_question_data_cy
    else:
        address = "BBC, W1A 1AA"
        form_names = ["organisation-information", "project-information"]
        question_data = test_question_data
    sections_put = [
        {
            "questions": question_data,
            "metadata": {
                "application_id": application.id,
                "form_name": form_names[0],
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
                            "answer": address,
                        },
                    ],
                },
            ],
            "metadata": {
                "application_id": application.id,
                "form_name": form_names[1],
                "is_summary_page_submit": False,
            },
        },
    ]
    # Make the org names unique
    sections_put[0]["questions"][1]["fields"][0]["answer"] = f"Test Org Name {unique_append}"

    for section in sections_put:
        client.put(
            "/applications/forms",
            json=section,
            follow_redirects=True,
        )


@pytest.fixture(scope="function")
def seed_data_multiple_funds_rounds(request, mocker, app, clear_test_data, enable_preserve_test_data, client):
    """
    Alternative to seed_application_records above that allows you to specify
    a set of funds/rounds and how many applications per round to allow
    testing of reporting functions. Expects to find fund/round config as a
    marker named 'fund_round_config' in the format:
    {funds: [rounds: [{applications: [{app_data}]}]]}

    yields a data structure containing the generated IDs:
    {[(fund_id: xxx, round_ids: [(round_id: yyy,
        application_ids: [111, 222])])]}
    """
    marker = request.node.get_closest_marker("fund_round_config")
    if marker is None:
        config = {"funds": [{"rounds": [{"applications": [test_application_data[0]]}]}]}
    else:
        config = marker.args[0]

    from collections import namedtuple

    FundRound = namedtuple("FundRound", "fund_id round_ids")
    RoundApps = namedtuple("RoundApps", "round_id application_ids")
    funds_rounds = []
    for fund in config["funds"]:
        fund_id = str(uuid4())
        round_ids = []
        for round in fund["rounds"]:
            round_id = str(uuid4())
            i = 0
            application_ids = []
            for appl in round["applications"]:
                i += 1
                appl["fund_id"] = fund_id
                appl["round_id"] = round_id
                created_app = create_app_with_blank_forms(appl)
                add_org_data_for_reports(created_app, i, client)
                application_ids.append(created_app.id)
            round_ids.append(RoundApps(round_id, application_ids))
        funds_rounds.append(FundRound(fund_id, round_ids))
    yield funds_rounds


def mock_get_data(endpoint, params=None):
    return local_api_call(endpoint, params, "get")


def mock_post_data(endpoint, params=None):
    return local_api_call(endpoint, params, "post")


def mock_get_random_choices(population, weights=None, *, cum_weights=None, k=1):
    return "ABCDEF"


def generate_mock_fund(fund_id: str) -> Fund:
    return Fund(
        "Generated test fund", fund_id, "TEST", "Testing fund", True, {"en": "English title", "cy": "Welsh title"}, []
    )


@pytest.fixture(scope="function", autouse=True)
def mock_get_fund(mocker):
    """
    Generates a mock fund with the supplied fund ID.
    Used with unique_fund_round to ensure when the fund and
    round are retrieved, they match what's expected
    """
    mocker.patch("api.routes.application.routes.get_fund", new=generate_mock_fund)
    mocker.patch("db.queries.application.queries.get_fund", new=generate_mock_fund)


@pytest.fixture(scope="function")
def mock_get_application_display_config(mocker):
    mocker.patch(
        "_helpers.form.get_application_sections",
        return_value=APPLICATION_DISPLAY_CONFIG,
    )


def generate_mock_round(fund_id: str, round_id: str) -> Round:
    return Round(
        title="Generated test round",
        id=round_id,
        fund_id=fund_id,
        short_name="TEST",
        opens=datetime.strptime("2023-01-01 12:00:00", "%Y-%m-%d %H:%M:%S"),
        deadline=datetime.strptime("2023-01-31 12:00:00", "%Y-%m-%d %H:%M:%S"),
        assessment_deadline=datetime.strptime("2023-03-31 12:00:00", "%Y-%m-%d %H:%M:%S"),
        project_name_field_id="TestFieldId",
        contact_email="test@outlook.com",
        title_json={"en": "English title", "cy": "Welsh title"},
    )


@pytest.fixture(scope="function", autouse=True)
def mock_get_round(mocker):
    """
    Generates a mock round with the supplied fund and round IDs
    Used with unique_fund_round to ensure when the fund and
    round are retrieved, they match what's expected
    """
    mocker.patch("db.queries.application.queries.get_round", new=generate_mock_round)
    mocker.patch("db.queries.statuses.queries.get_round", new=generate_mock_round)
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
        lambda template, email, full_name, application: Response(200),
    )


@pytest.fixture(autouse=True)
def mock_post_data_fix(mocker):
    # mock the function in the file it is invoked (not where it is declared)
    mocker.patch(
        "external_services.post_data",
        new=mock_post_data,
    )


@pytest.fixture(autouse=False)
def mock_get_fund_data(mocker):
    mocker.patch(
        "api.routes.application.routes.get_fund",
        return_value=Fund(
            name="COF",
            short_name="COF",
            identifier="47aef2f5-3fcb-4d45-acb5-f0152b5f03c4",
            description="An example fund for testing the funding service",
            welsh_available=False,
            name_json={"en": "English Fund Name", "cy": "Welsh Fund Name"},
        ),
    )


@pytest.fixture(autouse=False)
def mocked_get_fund(mocker):
    return mocker.patch(
        "scripts.send_application_on_closure.get_fund",
        return_value=Fund(
            name="Community Ownership Fund",
            identifier="47aef2f5-3fcb-4d45-acb5-f0152b5f03c4",
            short_name="COF",
            description=(
                "The Community Ownership Fund is a £150 million fund over 4 years to"
                " support community groups across England, Wales, Scotland and Northern"
                " Ireland to take ownership of assets which are at risk of being lost"
                " to the community."
            ),
            welsh_available=True,
            name_json={"en": "English Fund Name", "cy": "Welsh Fund Name"},
            rounds=None,
        ),
    )


@pytest.fixture(autouse=False)
def mock_submit_message_to_queue(mocker, request):
    function_calls_to_mock_marker = request.node.get_closest_marker("function_calls_to_mock")
    function_calls_to_mock = (
        function_calls_to_mock_marker.args[0]
        if function_calls_to_mock_marker
        else [
            "api.routes.application.routes._SQS_CLIENT.submit_single_message",
            "api.routes.queues.routes._SQS_CLIENT.submit_single_message",
        ]
    )

    application_id = "application_id_test"

    mocked_calls = []
    for mock_func in function_calls_to_mock:
        mock = mocker.patch(mock_func, return_value=application_id)
        mocked_calls.append(mock)

    yield mocked_calls

    if function_calls_to_mock_marker:
        for mock in mocked_calls:
            assert mock.called == True  # noqa
            assert len(mock.call_args[1]) == 5
