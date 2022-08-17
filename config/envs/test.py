"""Flask configuration."""
from os import environ

from config.envs.default import DefaultConfig
from fsd_utils import configclass
from os import environ

@configclass
class TestConfig(DefaultConfig):

    # Add any test specific config here

    # Database
    SQLALCHEMY_DATABASE_URI = environ.get("DATABASE_URL").replace(
        "postgres://", "postgresql://"
    )

    FUND_ROUND_FORMS = {
        "fund-a:spring": DefaultConfig.COF_R2_FORMS.copy(),
        "fund-b:spring": DefaultConfig.COF_R2_FORMS.copy(),
        "fund-a:summer": DefaultConfig.COF_R2_FORMS.copy(),
        "fund-b:summer": DefaultConfig.COF_R2_FORMS.copy(),
        "funding-service-design:spring": DefaultConfig.COF_R2_FORMS.copy(),
        "funding-service-design:summer": DefaultConfig.COF_R2_FORMS.copy(),
    }
