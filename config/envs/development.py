"""Flask configuration."""

import logging

from fsd_utils import configclass

from config.envs.default import DefaultConfig


@configclass
class DevelopmentConfig(DefaultConfig):
    FSD_LOGGING_LEVEL = logging.DEBUG
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "dev"  # pragma: allowlist secret
