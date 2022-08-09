from os import getenv
import pytest
from app import create_app
from db import db, migrate


@pytest.fixture(scope="session")
def app():
    """
    Creates the test client we will be using to test the responses
    from our app, this is a test fixture.
    :return: A flask test client.
    """
    app = create_app()
    migrate.upgrade()
    return app

@pytest.fixture(scope='session')
def _db(app):
    '''
    Provide the transactional fixtures with access to the database via a Flask-SQLAlchemy
    database connection.
    '''
    return db

@pytest.fixture(autouse=True)
def enable_transactional_tests(db_session):
    pass