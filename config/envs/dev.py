"""Flask configuration."""
import logging
from os import environ
from os import path

from config.envs.default import DefaultConfig
from fsd_utils import configclass


@configclass
class DevConfig(DefaultConfig):

    FSD_LOGGING_LEVEL = logging.INFO

    # Database
    SQLALCHEMY_DATABASE_URI = environ.get(
        "DATABASE_URL"
    ) or "sqlite:///" + path.join(DefaultConfig.FLASK_ROOT, "sqlite.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
