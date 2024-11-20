"""Flask configuration."""

import logging
from os import environ

from fsd_utils import configclass

from config.envs.default import DefaultConfig


@configclass
class DevConfig(DefaultConfig):
    FSD_LOGGING_LEVEL = logging.INFO
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SQLALCHEMY_DATABASE_URI = environ.get("DATABASE_URL").replace("postgres://", "postgresql://")
