"""Flask configuration."""
import logging
from os import environ
from os import path

from config.envs.default import DefaultConfig
from fsd_utils import configclass


@configclass
class DevelopmentConfig(DefaultConfig):

    FSD_LOGGING_LEVEL = logging.DEBUG

    SQLITE_DB_NAME = "sqlite.db"
    SQLALCHEMY_DATABASE_URI = environ.get(
        "DATABASE_URL"
    ) or "sqlite:///" + path.join(DefaultConfig.FLASK_ROOT, SQLITE_DB_NAME)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    FUND_ROUND_FORMS = {
        **DefaultConfig.FUND_ROUND_FORMS,
        "fund-a:spring": DefaultConfig.COF_R2_FORMS.copy(),
        "fund-b:spring": DefaultConfig.COF_R2_FORMS.copy(),
        "fund-a:summer": DefaultConfig.COF_R2_FORMS.copy(),
        "fund-b:summer": DefaultConfig.COF_R2_FORMS.copy(),
        "funding-service-design:spring": DefaultConfig.COF_R2_FORMS.copy(),
        "funding-service-design:summer": DefaultConfig.COF_R2_FORMS.copy(),
    }
