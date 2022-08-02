"""Flask Unit Testing Environment Configuration."""
from os import path

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
    SQLITE_DB_NAME = "test_sqlite.db"
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + path.join(
        DefaultConfig.FLASK_ROOT, SQLITE_DB_NAME
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
