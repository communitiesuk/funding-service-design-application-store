"""Flask configuration."""
from os import environ
from os import path

#  Application Config
SECRET_KEY = environ.get("SECRET_KEY") or "dev"
SESSION_COOKIE_NAME = environ.get("SESSION_COOKIE_NAME") or "session_cookie"
FLASK_ROOT = path.dirname(path.realpath(__file__))
FLASK_ENV = environ.get("FLASK_ENV") or "development"

#  APIs
TEST_FUND_STORE_API_HOST = "fund_store"
TEST_ACCOUNT_STORE_API_HOST = "account_store"
TEST_NOTIFICATION_SERVICE_HOST = "notification_service"

FUND_STORE_API_HOST = (
    environ.get("FUND_STORE_API_HOST") or TEST_FUND_STORE_API_HOST
)
ACCOUNT_STORE_API_HOST = (
    environ.get("ACCOUNT_STORE_API_HOST") or TEST_ACCOUNT_STORE_API_HOST
)

# Notification Service
NOTIFICATION_SERVICE_HOST = (
    environ.get("NOTIFICATION_SERVICE_HOST") or TEST_NOTIFICATION_SERVICE_HOST
)
SEND_ENDPOINT = "/send"
NOTIFY_TEMPLATE_SUBMIT_APPLICATION = "APPLICATION_RECORD_OF_SUBMISSION"

# Account Store Endpoints
ACCOUNTS_ENDPOINT = "/accounts"

# Fund Store Endpoints
FUNDS_ENDPOINT = "/funds"
FUND_ENDPOINT = "/funds/{fund_id}"
FUND_ROUNDS_ENDPOINT = "/funds/{fund_id}/rounds"
FUND_ROUND_ENDPOINT = "/funds/{fund_id}/rounds/{round_id}"
