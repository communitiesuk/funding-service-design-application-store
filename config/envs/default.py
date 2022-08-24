"""Flask configuration."""
import logging
from os import environ
from pathlib import Path

from fsd_utils import configclass


@configclass
class DefaultConfig:

    #  Application Config
    SECRET_KEY = environ.get("SECRET_KEY") or "dev"
    SESSION_COOKIE_NAME = environ.get("SESSION_COOKIE_NAME", "session_cookie")
    FLASK_ROOT = str(Path(__file__).parent.parent.parent)
    FLASK_ENV = environ.get("FLASK_ENV") or "development"

    FSD_LOGGING_LEVEL = logging.WARN

    #  APIs
    TEST_FUND_STORE_API_HOST = "fund_store"
    TEST_ACCOUNT_STORE_API_HOST = "account_store"
    TEST_NOTIFICATION_SERVICE_HOST = "notification_service"
    USE_LOCAL_DATA = False

    FUND_STORE_API_HOST = environ.get(
        "FUND_STORE_API_HOST", TEST_FUND_STORE_API_HOST
    )
    ACCOUNT_STORE_API_HOST = environ.get(
        "ACCOUNT_STORE_API_HOST", TEST_ACCOUNT_STORE_API_HOST
    )

    # Notification Service
    NOTIFICATION_SERVICE_HOST = environ.get(
        "NOTIFICATION_SERVICE_HOST", TEST_NOTIFICATION_SERVICE_HOST
    )

    SEND_ENDPOINT = "/send"
    NOTIFY_TEMPLATE_SUBMIT_APPLICATION = "APPLICATION_RECORD_OF_SUBMISSION"

    # Account Store Endpoints
    ACCOUNTS_ENDPOINT = "/accounts"

    # Fund Store Endpoints
    FUNDS_ENDPOINT = "/funds"
    FUND_ENDPOINT = "/funds/{fund_id}"
    FUND_ROUNDS_ENDPOINT = "/funds/{fund_id}/rounds"
    FUND_ROUND_ENDPOINT = "/funds/{fund_id}/rounds/{round_id}"

    SQLALCHEMY_DATABASE_URI = environ.get("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # COF FORMS BASE CONFIG
    COF_R2_FORMS = [
        {
            "form_minting_name": "applicant-information",
            "questions": [],
        },
        {
            "form_minting_name": "asset-information",
            "questions": [],
        },
        {
            "form_minting_name": "community-benefits",
            "questions": [],
        },
        {
            "form_minting_name": "community-engagement",
            "questions": [],
        },
        {
            "form_minting_name": "community-representation",
            "questions": [],
        },
        {
            "form_minting_name": "community-use",
            "questions": [],
        },
        {
            "form_minting_name": "declarations",
            "questions": [],
        },
        {
            "form_minting_name": "environmental-sustainability",
            "questions": [],
        },
        {
            "form_minting_name": "feasibility",
            "questions": [],
        },
        {
            "form_minting_name": "funding-required",
            "questions": [],
        },
        {
            "form_minting_name": "inclusiveness-and-intergration",
            "questions": [],
        },
        {
            "form_minting_name": "local-support",
            "questions": [],
        },
        {
            "form_minting_name": "organisation-information",
            "questions": [],
        },
        {
            "form_minting_name": "project-costs",
            "questions": [],
        },
        {
            "form_minting_name": "project-information",
            "questions": [],
        },
        {
            "form_minting_name": "project-qualification",
            "questions": [],
        },
        {
            "form_minting_name": "risk",
            "questions": [],
        },
        {
            "form_minting_name": "skills-and-resources",
            "questions": [],
        },
        {
            "form_minting_name": "value-to-the-community",
            "questions": [],
        },
        {
            "form_minting_name": "upload-business-plan",
            "questions": [],
        },
    ]

    COF_FUND_ID = "47aef2f5-3fcb-4d45-acb5-f0152b5f03c4"
    COF_ROUND_2_ID = "c603d114-5364-4474-a0c4-c41cbf4d3bbd"
    FUND_ROUND_FORMS = {
        f"{COF_FUND_ID}:{COF_ROUND_2_ID}": COF_R2_FORMS.copy(),
    }
