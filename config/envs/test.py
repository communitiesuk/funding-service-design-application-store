"""Flask configuration."""
from os import environ

from config.envs.default import DefaultConfig
from fsd_utils import configclass


@configclass
class TestConfig(DefaultConfig):

    # Add any test specific config here

    SQLALCHEMY_DATABASE_URI = environ.get("DATABASE_URL").replace(
        "postgres://", "postgresql://"
    )

    ASSESSMENT_FRONTEND_URL = "fsd:fsd@assessment.test.gids.dev"
