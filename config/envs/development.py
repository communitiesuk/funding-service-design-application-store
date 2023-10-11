"""Flask configuration."""
import logging

from config.envs.default import DefaultConfig
from fsd_utils import configclass


@configclass
class DevelopmentConfig(DefaultConfig):

    FSD_LOGGING_LEVEL = logging.DEBUG
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    ASSESSMENT_FRONTEND_URL = "localhost:3010"
