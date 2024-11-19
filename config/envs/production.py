"""Flask configuration."""

from os import environ

from fsd_utils import configclass

from config.envs.default import DefaultConfig


@configclass
class ProductionConfig(DefaultConfig):
    SQLALCHEMY_DATABASE_URI = environ.get("DATABASE_URL").replace("postgres://", "postgresql://")
