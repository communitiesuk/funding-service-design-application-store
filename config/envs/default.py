"""Flask configuration."""
import logging
import os
from os import environ
from pathlib import Path

from distutils.util import strtobool
from fsd_utils import CommonConfig
from fsd_utils import configclass


@configclass
class DefaultConfig:
    #  Application Config
    FLASK_ENV = CommonConfig.FLASK_ENV
    SECRET_KEY = CommonConfig.SECRET_KEY
    SESSION_COOKIE_NAME = environ.get("SESSION_COOKIE_NAME", "session_cookie")
    FLASK_ROOT = str(Path(__file__).parent.parent.parent)

    FSD_LOGGING_LEVEL = logging.WARN

    #  APIs
    TEST_FUND_STORE_API_HOST = "fund_store"
    TEST_ACCOUNT_STORE_API_HOST = "account_store"
    USE_LOCAL_DATA = strtobool(environ.get("USE_LOCAL_DATA", "False"))

    FUND_STORE_API_HOST = environ.get("FUND_STORE_API_HOST", TEST_FUND_STORE_API_HOST)
    ACCOUNT_STORE_API_HOST = environ.get("ACCOUNT_STORE_API_HOST", TEST_ACCOUNT_STORE_API_HOST)

    # Notification Service
    NOTIFY_TEMPLATE_SUBMIT_APPLICATION = "APPLICATION_RECORD_OF_SUBMISSION"
    NOTIFY_TEMPLATE_INCOMPLETE_APPLICATION = "INCOMPLETE_APPLICATION_RECORDS"
    NOTIFY_TEMPLATE_APPLICATION_DEADLINE_REMINDER = "APPLICATION_DEADLINE_REMINDER"
    NOTIFY_TEMPLATE_APPLICATION_DEADLINE_REMINDER = environ.get(
        "NOTIFY_TEMPLATE_APPLICATION_DEADLINE_REMINDER",
        NOTIFY_TEMPLATE_APPLICATION_DEADLINE_REMINDER,
    )
    NOTIFY_TEMPLATE_EOI_PASS = "Full pass"
    NOTIFY_TEMPLATE_EOI_PASS_W_CAVEATS = "Pass with caveats"

    if "PRIMARY_QUEUE_URL" in os.environ:
        AWS_REGION = AWS_SQS_REGION = os.environ.get("AWS_REGION")
        AWS_BUCKET_NAME = os.environ.get("AWS_BUCKET_NAME")
        AWS_SQS_IMPORT_APP_PRIMARY_QUEUE_URL = os.environ.get("PRIMARY_QUEUE_URL")
        AWS_SQS_IMPORT_APP_SECONDARY_QUEUE_URL = os.environ.get("DEAD_LETTER_QUEUE_URL")
    else:
        AWS_ACCESS_KEY_ID = AWS_SQS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
        AWS_SECRET_ACCESS_KEY = AWS_SQS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
        AWS_BUCKET_NAME = os.environ.get("AWS_BUCKET_NAME")
        AWS_REGION = AWS_SQS_REGION = os.environ.get("AWS_REGION")
        AWS_SQS_IMPORT_APP_PRIMARY_QUEUE_URL = os.environ.get("AWS_SQS_IMPORT_APP_PRIMARY_QUEUE_URL")
        AWS_SQS_IMPORT_APP_SECONDARY_QUEUE_URL = os.environ.get("AWS_SQS_IMPORT_APP_SECONDARY_QUEUE_URL")

    # Account Store Endpoints
    ACCOUNTS_ENDPOINT = "/accounts"

    # Fund Store Endpoints
    FUNDS_ENDPOINT = CommonConfig.FUNDS_ENDPOINT
    FUND_ENDPOINT = CommonConfig.FUND_ENDPOINT
    FUND_ROUNDS_ENDPOINT = CommonConfig.ROUNDS_ENDPOINT
    FUND_ROUND_ENDPOINT = CommonConfig.ROUND_ENDPOINT
    FUND_ROUND_APPLICATION_SECTIONS_ENDPOINT = (
        "/funds/{fund_id}/rounds/{round_id}/sections/application?language={language}"
    )
    FUND_ROUND_APPLICATION_REMINDER_STATUS = "/funds/{round_id}/application_reminder_status?status=true"
    FUND_ROUND_EOI_SCHEMA_ENDPOINT = FUND_STORE_API_HOST + "/funds/{fund_id}/rounds/{round_id}/eoi_decision_schema"

    SQLALCHEMY_DATABASE_URI = environ.get("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"future": True}
    DOCUMENT_UPLOAD_SIZE_LIMIT = 2 * 1024 * 1024

    # ---------------
    # AWS Overall Config
    # ---------------
    AWS_ACCESS_KEY_ID = AWS_SQS_ACCESS_KEY_ID = environ.get("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = AWS_SQS_SECRET_ACCESS_KEY = environ.get("AWS_SECRET_ACCESS_KEY")
    AWS_REGION = AWS_SQS_REGION = environ.get("AWS_REGION")
    AWS_ENDPOINT_OVERRIDE = environ.get("AWS_ENDPOINT_OVERRIDE")

    # ---------------
    # S3 Config
    # ---------------
    AWS_MSG_BUCKET_NAME = environ.get("AWS_MSG_BUCKET_NAME")

    # ---------------
    # SQS Config
    # ---------------
    AWS_SQS_NOTIF_APP_PRIMARY_QUEUE_URL = environ.get("AWS_SQS_NOTIF_APP_PRIMARY_QUEUE_URL")
    AWS_SQS_NOTIF_APP_SECONDARY_QUEUE_URL = environ.get("AWS_SQS_NOTIF_APP_SECONDARY_QUEUE_URL")
