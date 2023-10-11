"""Flask configuration."""
import logging
from os import environ

from config.envs.default import DefaultConfig
from fsd_utils import configclass


@configclass
class DevConfig(DefaultConfig):

    FSD_LOGGING_LEVEL = logging.INFO
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SQLALCHEMY_DATABASE_URI = environ.get("DATABASE_URL").replace(
        "postgres://", "postgresql://"
    )
