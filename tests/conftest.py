import pytest
from app import create_app
from db import db
from flask import Response
from flask_migrate import upgrade
from tests.helpers import local_api_call

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
    with app.app_context():
        upgrade()
        conn = db.engine.connect()
        nt = conn.begin_nested()

        yield app

        nt.rollback()
        nt.close()

    # with app.app_context():
    #     upgrade()
    #     # engines = db.engines

    # # engine_cleanup = []

    #     engine = db.engine
    # # for key, engine in engines.items():
    # # connection = engine.connect()
    # # transaction = connection.begin()
    # # session = db.create_scoped_session()
    #     session = db.session
    # # db.engine = connection
    # # engine_cleanup.append((key, engine, connection, transaction))

    #     yield app

    # # for key, engine, connection, transaction in engine_cleanup:
    # # transaction.rollback()
    # # connection.close()
    # # db.engine = engine
    #     session.rollback()


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


# @pytest.fixture(scope="session")
# def _db(app):
#     """
#     Provide the transactional fixtures with access
#     to the database via a Flask-SQLAlchemy
#     database connection.
#     """
#     return db


# @pytest.fixture(autouse=True)
# def enable_transactional_tests(db_session):
#     pass
