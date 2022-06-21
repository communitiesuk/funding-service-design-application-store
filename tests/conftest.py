import pytest
from app import create_app
import os


@pytest.fixture()
def flask_test_client():
    """
    Creates the test client we will be using to test the responses
    from our app, this is a test fixture.
    :return: A flask test client.
    """
    os.environ["FLASK_ENV"] = "test"
    with create_app().test_client() as test_client:
        yield test_client
