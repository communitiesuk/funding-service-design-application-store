"""Flask Unit Testing Environment Configuration."""
from os import environ

from config.envs.default import DefaultConfig
from fsd_utils import CommonConfig
from fsd_utils import configclass


@configclass
class UnitTestingConfig(DefaultConfig):
    #  Application Config
    SECRET_KEY = "dev"
    SESSION_COOKIE_NAME = CommonConfig.SESSION_COOKIE_NAME
    FLASK_ENV = "unit_test"
    FUND_STORE_API_HOST = DefaultConfig.TEST_FUND_STORE_API_HOST

    # Security
    FORCE_HTTPS = False

    # Database
    SQLALCHEMY_DATABASE_URI = environ.get(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/postgres",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    FUND_ROUND_FORMS = {
        "fund-a:spring": DefaultConfig.COF_R2_FORMS.copy(),
        "fund-b:spring": DefaultConfig.COF_R2_FORMS.copy(),
        "47aef2f5-3fcb-4d45-acb5-f0152b5f03c4:c603d114-5364-4474-a0c4-c41cbf4d3bbd": DefaultConfig.COF_R2_FORMS.copy(),  # noqa
        "fund-b:summer": DefaultConfig.COF_R2_FORMS.copy(),
        "funding-service-design:spring": DefaultConfig.COF_R2_FORMS.copy(),
        "funding-service-design:summer": DefaultConfig.COF_R2_FORMS.copy(),
    }

    USE_LOCAL_DATA = True
