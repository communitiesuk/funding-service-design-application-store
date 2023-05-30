# flake8 : noqa
"""Flask Unit Testing Environment Configuration."""
from os import environ

from config.envs.default import DefaultConfig
from fsd_utils import configclass
from fsd_utils.config.commonconfig import CommonConfig


@configclass
class UnitTestingConfig(DefaultConfig):
    #  Application Config
    SECRET_KEY = "dev"
    SESSION_COOKIE_NAME = CommonConfig.SESSION_COOKIE_NAME
    FLASK_ENV = "unit_test"
    FUND_STORE_API_HOST = DefaultConfig.TEST_FUND_STORE_API_HOST

    # Security
    FORCE_HTTPS = False

    # Database
    SQLALCHEMY_DATABASE_URI = environ.get(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/fsd_app_store_test",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    USE_LOCAL_DATA = True
