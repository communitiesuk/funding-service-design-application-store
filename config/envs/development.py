"""Flask configuration."""
import logging
from os import environ

from config.envs.default import DefaultConfig
from fsd_utils import configclass


@configclass
class DevelopmentConfig(DefaultConfig):

    FSD_LOGGING_LEVEL = logging.DEBUG
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    AWS_ENDPOINT_OVERRIDE = environ.get("AWS_ENDPOINT_OVERRIDE")
