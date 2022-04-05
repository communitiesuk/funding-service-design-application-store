"""Flask configuration."""
from os import environ
from os import path

"""
Application Config
"""
SECRET_KEY = environ.get("SECRET_KEY") or "dev"
SESSION_COOKIE_NAME = environ.get("SESSION_COOKIE_NAME") or "session_cookie"
FLASK_ROOT = path.dirname(path.realpath(__file__))
FLASK_ENV = environ.get("FLASK_ENV") or "development"

"""
APIs Config
"""
TEST_FUND_STORE_API_HOST = "fund_store"
TEST_ROUND_STORE_API_HOST = "round_store"

FUND_STORE_API_HOST = (
    environ.get("FUND_STORE_API_HOST") or TEST_FUND_STORE_API_HOST
)
ROUND_STORE_API_HOST = (
    environ.get("ROUND_STORE_API_HOST") or TEST_ROUND_STORE_API_HOST
)
