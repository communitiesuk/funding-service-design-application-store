"""Flask Unit Testing Environment Configuration."""
from os import environ, path

from config.envs.default import DefaultConfig
from fsd_utils import CommonConfig
from fsd_utils import configclass


@configclass
class UnitTestingConfig(DefaultConfig):
    #  Application Config
    SECRET_KEY = "dev"
    SESSION_COOKIE_NAME = CommonConfig.SESSION_COOKIE_NAME
    FLASK_ENV = "unit_test"

    # Security
    FORCE_HTTPS = False

    # Database
    SQLALCHEMY_DATABASE_URI = environ.get("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/postgres").replace(
        "postgres://", "postgresql://"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
