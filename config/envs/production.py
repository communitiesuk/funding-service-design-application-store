"""Flask configuration."""
from os import environ

from config.envs.default import DefaultConfig
from fsd_utils import configclass


@configclass
class ProductionConfig(DefaultConfig):

    SQLALCHEMY_DATABASE_URI = environ.get("DATABASE_URL").replace(
        "postgres://", "postgresql://"
    )
