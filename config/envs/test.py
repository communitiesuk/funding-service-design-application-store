"""Flask configuration."""

from os import environ

from fsd_utils import configclass

from config.envs.default import DefaultConfig


@configclass
class TestConfig(DefaultConfig):
    # Add any test specific config here

    SQLALCHEMY_DATABASE_URI = environ.get("DATABASE_URL").replace("postgres://", "postgresql://")
