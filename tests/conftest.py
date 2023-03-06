import pytest
from app import create_app
from db import db
from flask import Response
from flask_migrate import upgrade
from tests.helpers import local_api_call


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
    return app


@pytest.fixture(scope="session")
def _db(app):
    """
    Provide the transactional fixtures with access
    to the database via a Flask-SQLAlchemy
    database connection.
    """
    return db


@pytest.fixture(scope="function")
def _transaction(request, _db):
    """
    Overrides the default pytest-flask-sqlalchemy fixture `_transaction`
    due to issues with the recent upgrade from version 2.5.1 to 3.0.3.
    Provides a transactional database session with a connection,
    transaction and session objects.

    Args:
    request: the pytest request object.
    _db: the pytest fixture that provides access to the database.

    return: a tuple containing the connection, transaction
    and session objects.
    """
    connection = _db.engine.connect()
    transaction = connection.begin()

    options = dict(bind=connection, binds={})
    # create a session with "_make_scoped_session"
    session = _db._make_scoped_session(options=options)

    def teardown():
        transaction.rollback()
        connection.close()
        session.remove()

    request.addfinalizer(teardown)

    return connection, transaction, session


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

    with _db.engine.connect() as connection:
        # disable foreign key checks
        connection.execute("SET session_replication_role = replica")
        # delete all data from tables
        for table in reversed(db.metadata.sorted_tables):
            connection.execute(table.delete())
        # reset foreign key checks
        connection.execute("SET session_replication_role = DEFAULT")


@pytest.fixture(autouse=True)
def enable_transactional_tests(db_session):
    pass


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
