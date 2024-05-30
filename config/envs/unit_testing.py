# flake8 : noqa
"""Flask Unit Testing Environment Configuration."""
from os import environ

from config.envs.default import DefaultConfig
from fsd_utils import configclass
from fsd_utils.config.commonconfig import CommonConfig


@configclass
class UnitTestingConfig(DefaultConfig):
    #  Application Config
    SECRET_KEY = "dev"  # pragma: allowlist secret
    SESSION_COOKIE_NAME = CommonConfig.SESSION_COOKIE_NAME
    FLASK_ENV = "unit_test"
    FUND_STORE_API_HOST = DefaultConfig.TEST_FUND_STORE_API_HOST

    # Security
    FORCE_HTTPS = False

    # Database
    SQLALCHEMY_DATABASE_URI = environ.get(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/fsd_app_store_test",  # pragma: allowlist secret
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    AWS_SQS_SECRET_ACCESS_KEY = ""
    AWS_SQS_ACCESS_KEY_ID = ""
    USE_LOCAL_DATA = True
    AWS_SQS_IMPORT_APP_PRIMARY_QUEUE_URL = "fsd-queue-test"
    AWS_SQS_REGION = "eu-west-2"

    # ---------------
    # S3 Config
    # ---------------
    AWS_MSG_BUCKET_NAME = "fsd-notification-bucket"
