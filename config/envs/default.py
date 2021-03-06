"""Flask configuration."""
import logging
from os import environ
from pathlib import Path

from fsd_utils import configclass


@configclass
class DefaultConfig:

    #  Application Config
    SECRET_KEY = environ.get("SECRET_KEY") or "dev"
    SESSION_COOKIE_NAME = environ.get("SESSION_COOKIE_NAME", "session_cookie")
    FLASK_ROOT = str(Path(__file__).parent.parent.parent)
    FLASK_ENV = environ.get("FLASK_ENV") or "development"

    FSD_LOGGING_LEVEL = logging.WARN

    #  APIs
    TEST_FUND_STORE_API_HOST = "fund_store"
    TEST_ACCOUNT_STORE_API_HOST = "account_store"
    TEST_NOTIFICATION_SERVICE_HOST = "notification_service"

    FUND_STORE_API_HOST = environ.get(
        "FUND_STORE_API_HOST", TEST_FUND_STORE_API_HOST
    )
    ACCOUNT_STORE_API_HOST = environ.get(
        "ACCOUNT_STORE_API_HOST", TEST_ACCOUNT_STORE_API_HOST
    )

    # Notification Service
    NOTIFICATION_SERVICE_HOST = environ.get(
        "NOTIFICATION_SERVICE_HOST", TEST_NOTIFICATION_SERVICE_HOST
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
