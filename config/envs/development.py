"""Flask configuration."""
import logging
from os import environ

from config.envs.default import DefaultConfig
from fsd_utils import configclass


@configclass
class DevelopmentConfig(DefaultConfig):

    SQLALCHEMY_DATABASE_URI = environ.get("DATABASE_URL")
    FSD_LOGGING_LEVEL = logging.DEBUG
    SQLALCHEMY_TRACK_MODIFICATIONS = False
