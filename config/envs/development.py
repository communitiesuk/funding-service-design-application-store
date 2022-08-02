"""Flask configuration."""
import logging

from config.envs.default import DefaultConfig
from fsd_utils import configclass


@configclass
class DevelopmentConfig(DefaultConfig):

    FSD_LOGGING_LEVEL = logging.DEBUG

    SQLITE_DB_NAME = "sqlite.db"
    SQLALCHEMY_DATABASE_URI = environ.get(
        "DATABASE_URL"
    ) or "sqlite:///" + path.join(DefaultConfig.FLASK_ROOT, SQLITE_DB_NAME)
    SQLALCHEMY_TRACK_MODIFICATIONS = False