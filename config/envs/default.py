"""Flask configuration."""
import json
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
    SECRET_KEY = environ.get("SECRET_KEY") or "dev"
    SESSION_COOKIE_NAME = environ.get("SESSION_COOKIE_NAME", "session_cookie")
    FLASK_ROOT = str(Path(__file__).parent.parent.parent)
    FLASK_ENV = environ.get("FLASK_ENV") or "development"

    FSD_LOGGING_LEVEL = logging.WARN

    #  APIs
    TEST_FUND_STORE_API_HOST = "fund_store"
    TEST_ACCOUNT_STORE_API_HOST = "account_store"
    TEST_NOTIFICATION_SERVICE_HOST = "notification_service"
    USE_LOCAL_DATA = strtobool(environ.get("USE_LOCAL_DATA", "False"))

    FUND_STORE_API_HOST = environ.get("FUND_STORE_API_HOST", TEST_FUND_STORE_API_HOST)
    ACCOUNT_STORE_API_HOST = environ.get(
        "ACCOUNT_STORE_API_HOST", TEST_ACCOUNT_STORE_API_HOST
    )

    # Notification Service
    NOTIFICATION_SERVICE_HOST = environ.get(
        "NOTIFICATION_SERVICE_HOST", TEST_NOTIFICATION_SERVICE_HOST
    )

    SEND_ENDPOINT = "/send"
    NOTIFY_TEMPLATE_SUBMIT_APPLICATION = "APPLICATION_RECORD_OF_SUBMISSION"
    NOTIFY_TEMPLATE_INCOMPLETE_APPLICATION = "INCOMPLETE_APPLICATION_RECORDS"
    NOTIFY_TEMPLATE_APPLICATION_DEADLINE_REMINDER = "APPLICATION_DEADLINE_REMINDER"
    NOTIFY_TEMPLATE_APPLICATION_DEADLINE_REMINDER = environ.get(
        "NOTIFY_TEMPLATE_APPLICATION_DEADLINE_REMINDER",
        NOTIFY_TEMPLATE_APPLICATION_DEADLINE_REMINDER,
    )

    if "PRIMARY_QUEUE_URL" in os.environ:
        AWS_REGION = AWS_SQS_REGION = os.environ.get("AWS_REGION")
        AWS_BUCKET_NAME = os.environ.get("AWS_BUCKET_NAME")
        AWS_SQS_IMPORT_APP_PRIMARY_QUEUE_URL = os.environ.get("PRIMARY_QUEUE_URL")
        AWS_SQS_IMPORT_APP_SECONDARY_QUEUE_URL = os.environ.get("DEAD_LETTER_QUEUE_URL")
    elif "VCAP_SERVICES" in os.environ:
        vcap_services = json.loads(os.environ["VCAP_SERVICES"])

        if "aws-s3-bucket" in vcap_services:
            s3_credentials = vcap_services["aws-s3-bucket"][0]["credentials"]
            AWS_REGION = s3_credentials["aws_region"]
            AWS_ACCESS_KEY_ID = s3_credentials["aws_access_key_id"]
            AWS_SECRET_ACCESS_KEY = s3_credentials["aws_secret_access_key"]
            AWS_BUCKET_NAME = s3_credentials["bucket_name"]
        if "aws-sqs-queue" in vcap_services:
            sqs_credentials = vcap_services["aws-sqs-queue"][0]["credentials"]
            AWS_SQS_REGION = sqs_credentials["aws_region"]
            AWS_SQS_ACCESS_KEY_ID = sqs_credentials["aws_access_key_id"]
            AWS_SQS_SECRET_ACCESS_KEY = sqs_credentials["aws_secret_access_key"]
            AWS_SQS_IMPORT_APP_PRIMARY_QUEUE_URL = sqs_credentials["primary_queue_url"]
            AWS_SQS_IMPORT_APP_SECONDARY_QUEUE_URL = sqs_credentials[
                "secondary_queue_url"
            ]
    else:
        AWS_ACCESS_KEY_ID = AWS_SQS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
        AWS_SECRET_ACCESS_KEY = AWS_SQS_SECRET_ACCESS_KEY = os.environ.get(
            "AWS_SECRET_ACCESS_KEY"
        )
        AWS_BUCKET_NAME = os.environ.get("AWS_BUCKET_NAME")
        AWS_REGION = AWS_SQS_REGION = os.environ.get("AWS_REGION")
        AWS_SQS_IMPORT_APP_PRIMARY_QUEUE_URL = os.environ.get(
            "AWS_SQS_IMPORT_APP_PRIMARY_QUEUE_URL"
        )
        AWS_SQS_IMPORT_APP_SECONDARY_QUEUE_URL = os.environ.get(
            "AWS_SQS_IMPORT_APP_SECONDARY_QUEUE_URL"
        )

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
    FUND_ROUND_APPLICATION_REMINDER_STATUS = (
        "/funds/{round_id}/application_reminder_status?status=true"
    )

    SQLALCHEMY_DATABASE_URI = environ.get("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"future": True}
