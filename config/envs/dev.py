"""Flask configuration."""
import logging

from config.envs.default import DefaultConfig
from fsd_utils import configclass


@configclass
class DevConfig(DefaultConfig):

    FSD_LOGGING_LEVEL = logging.INFO
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    FUND_ROUND_FORMS = {
        "fund-a:spring": DefaultConfig.COF_R2_FORMS.copy(),
        "fund-b:spring": DefaultConfig.COF_R2_FORMS.copy(),
        "fund-a:summer": DefaultConfig.COF_R2_FORMS.copy(),
        "fund-b:summer": DefaultConfig.COF_R2_FORMS.copy(),
        "funding-service-design:spring": DefaultConfig.COF_R2_FORMS.copy(),
        "funding-service-design:summer": DefaultConfig.COF_R2_FORMS.copy(),
    }
