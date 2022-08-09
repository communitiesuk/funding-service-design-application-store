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
        "status": "NOT_STARTED",
        "form": "applicant-information",
        "questions": [
            {
                "question": "About your organisation",
                "fields": [
                    {
                        "key": "ZBjDTn",
                        "title": "Name of lead contact",
                        "type": "text",
                        "answer": "",
                    },
                    {
                        "key": "LZBrEj",
                        "title": "Lead contact email address",
                        "type": "text",
                        "answer": "",
                    },
                    {
                        "key": "lRfhGB",
                        "title": "Lead contact telephone number",
                        "type": "text",
                        "answer": "",
                    },
                ],
            },
        ],
    },
    {
        "status": "NOT_STARTED",
        "form": "asset-information",
        "questions": [
            {
                "question": "About your project",
                "fields": [
                    {
                        "key": "yaQoxU",
                        "title": "Asset type",
                        "type": "list",
                        "answer": ""
                    },
                ],
            },
            {
                "question": "About your project",
                "fields": [
                    {
                        "key": "VWkLlk",
                        "title": "What do you intend to do with the asset?",
                        "type": "list",
                        "answer": ""
                    },
                    {
                        "key": "IRfSZp",
                        "title": "Do you know who currently owns your asset?",
                        "type": "list",
                        "answer": ""
                    },
                ],
            },
            {
                "question": "About your project",
                "fields": [
                    {
                        "key": "FtDJfK",
                        "title": "Describe the current ownership status",
                        "type": "text",
                        "answer": ""
                    },
                ],
            },
            {
                "question": "About your project",
                "fields": [
                    {
                        "key": "gkulUE",
                        "title": "Is the asset currently for sale?",
                        "type": "list",
                        "answer": ""
                    },
                ],
            },
            {
                "question": "About your project",
                "fields": [
                    {
                        "key": "FXQwZT",
                        "title": "Describe the expected sale process, and whether the owner is currently willing to sell",
                        "type": "text",
                        "answer": ""
                    },
                    {
                        "key": "ghzLRv",
                        "title": "Expected date of sale",
                        "type": "date",
                        "answer": ""
                    },
                ],
            },
            {
                "question": "About your project",
                "fields": [
                    {
                        "key": "Wyesgy",
                        "title": "Is your asset currently publicly owned?",
                        "type": "list",
                        "answer": ""
                    },
                ],
            },
            {
                "question": "About your project",
                "fields": [
                    {
                        "key": "hvzzWB",
                        "title": "Is this a registered asset of community value (ACV)?",
                        "type": "list",
                        "answer": ""
                    },
                ],
            },
            {
                "question": "About your project",
                "fields": [
                    {
                        "key": "VwxiGn",
                        "title": "Is the asset listed for disposal, or part of a Community Asset Transfer?",
                        "type": "list",
                        "answer": ""
                    },
                ],
            },
            {
                "question": "About your project",
                "fields": [
                    {
                        "key": "UDTxqC",
                        "title": "Why is the asset at risk of closure?",
                        "type": "list",
                        "answer": ""
                    },
                ],
            },
        ],
    },
    {
        "status": "NOT_STARTED",
        "form": "community-benefits",
        "questions": [
            {
                "question": "Potential to deliver community benefits",
                "fields": [
                    {
                        "key": "QjJtbs",
                        "title": "What community benefits do you expect to deliver with this project?",
                        "type": "list",
                        "answer": "",
                    },
                    {
                        "key": "gDTsgG",
                        "title": "Tell us about these benefits in detail, and explain how you will measure the benefits it will bring for the community",
                        "type": "text",
                        "answer": "",
                    },
                    {
                        "key": "kYjJFy",
                        "title": "Explain how you will deliver and sustain these benefits over time",
                        "type": "text",
                        "answer": "",
                    },
                    {
                        "key": "UbjYqE",
                        "title": "Explain how community ownership of the asset will be inclusive and benefit the wider community",
                        "type": "text",
                        "answer": "",
                    },
                ],
            },
        ],
    },
    {
        "status": "NOT_STARTED",
        "form": "community-engagement",
        "questions": [
            {
                "question": "Strategic case",
                "fields": [
                    {
                        "key": "HJBgvw",
                        "title": "Tell us how you have engaged with the community about your intention to take ownership of the asset, and explain how this has shaped your project plans",
                        "type": "text",
                        "answer": "",
                    },
                    {
                        "key": "JCACTy",
                        "title": "Have you done any fundraising in the community?",
                        "type": "list",
                        "answer": "",
                    },
                ],
            },
            {
                "question": "Strategic case",
                "fields": [
                    {
                        "key": "NZKHOp",
                        "title": "Tell us how your project supports any wider local plans",
                        "type": "text",
                        "answer": "",
                    },
                ],
            },
        ],
    },
    {
        "status": "NOT_STARTED",
        "form": "community-representation",
        "questions": [
            {
                "question": "Management case",
                "fields": [
                    {
                        "key": "JnvsPq",
                        "title": "List the members of your board",
                        "type": "text",
                        "answer": "",
                    },
                    {
                        "key": "yMCivI",
                        "title": "Tell us about your governance and membership structures",
                        "type": "text",
                        "answer": "",
                    },
                    {
                        "key": "NUZOvS",
                        "title": "Explain how you will consider the views of the community in the running of the asset",
                        "type": "text",
                        "answer": "",
                    },
                ],
            },
        ],
    },
    {
        "status": "NOT_STARTED",
        "form": "community-use",
        "questions": [
            {
                "question": "Strategic case",
                "fields": [
                    {
                        "key": "CDwTrG",
                        "title": "What policy aims will your project deliver against?",
                        "type": "list",
                        "answer": "",
                    },
                    {
                        "key": "kxgWTy",
                        "title": "Who in the community uses the asset, or has used it in the past, and who benefits from it?",
                        "type": "text",
                        "answer": "",
                    },
                    {
                        "key": "SCyzGs",
                        "title": "Add another community user",
                        "type": "text",
                        "answer": "",
                    },
                    {
                        "key": "GNhrIs",
                        "title": "Tell us how losing the asset would affect, or has already affected, people in the community",
                        "type": "text",
                        "answer": "",
                    },
                    {
                        "key": "qsZLjZ",
                        "title": "Why will the asset be lost without community intervention?",
                        "type": "text",
                        "answer": "",
                    },
                ],
            },
        ],
    },
    {
        "status": "NOT_STARTED",
        "form": "declarations",
        "questions": [
            {
                "question": "Declarations",
                "fields": [
                    {
                        "key": "LlvhYl",
                        "title": "Confirm you have considered subsidy control / state aid implications for your project, and the information you have given us is correct",
                        "type": "list",
                        "answer": "",
                    },
                    {
                        "key": "wJrJWY",
                        "title": "Confirm you have considered people with protected characteristics throughout the planning of your project",
                        "type": "list",
                        "answer": "",
                    },
                    {
                        "key": "COiwQr",
                        "title": "Confirm you have considered sustainability and the environment throughout the planning of your project, including compliance with the government's Net Zero ambitions",
                        "type": "list",
                        "answer": "",
                    },
                ],
            },
        ],
    },
    {
        "status": "NOT_STARTED",
        "form": "environmental-sustainability",
        "questions": [
            {
                "question": "Strategic case",
                "fields": [
                    {
                        "key": "CvVZJv",
                        "title": "Tell us how you have considered the environmental sustainability of your project",
                        "type": "text",
                        "answer": "",
                    },
                ],
            },
        ],
    },
    {
        "status": "NOT_STARTED",
        "form": "feasibility",
        "questions": [
            {
                "question": "Management case",
                "fields": [
                    {
                        "key": "ieRCkI",
                        "title": "Tell us about the feasibility studies you have carried out for your project",
                        "type": "text",
                        "answer": "",
                    },
                    {
                        "key": "aAeszH",
                        "title": "Do you need to do any further feasibility work?",
                        "type": "list",
                        "answer": "",
                    },
                ],
            },
        ],
    },
    {
        "status": "NOT_STARTED",
        "form": "funding-required",
        "questions": [
            {
                "question": "Management case",
                "fields": [
                    {
                        "key": "yquoIb",
                        "title": "Have you already secured this (your match) funding?",
                        "type": "list",
                        "answer": "",
                    },
                ],
            },
            {
                "question": "Management case",
                "fields": [
                    {
                        "key": "fnIdkJ",
                        "title": "Asset value",
                        "type": "text",
                        "answer": "",
                    },
                ],
            },
        ],
    },
    {
        "status": "NOT_STARTED",
        "form": "inclusiveness-and-intergration",
        "questions": [
            {
                "question": "Management case",
                "fields": [
                    {
                        "key": "YbfbSC",
                        "title": "Describe anything that might prevent people from using the asset or participating in its running",
                        "type": "text",
                        "answer": "",
                    },
                    {
                        "key": "KuhSWw",
                        "title": "Tell us how you will make your project accessible and inclusive to everyone in the community",
                        "type": "text",
                        "answer": "",
                    },
                    {
                        "key": "bkJsiO",
                        "title": "Describe how the project will bring people together from all over the community",
                        "type": "text",
                        "answer": "",
                    },
                ],
            },
        ],
    },
    {
        "status": "NOT_STARTED",
        "form": "local-support",
        "questions": [
            {
                "question": "Strategic case",
                "fields": [
                    {
                        "key": "KqoaJL",
                        "title": "Is there local support for your project?",
                        "type": "list",
                        "answer": "",
                    },
                ],
            },
        ],
    },
    {
        "status": "NOT_STARTED",
        "form": "organisation-information",
        "questions": [
            {
                "question": "About your organisation",
                "fields": [
                    {
                        "key": "MhTuux",
                        "title": "Organisation name",
                        "type": "text",
                        "answer": "",
                    },
                    {
                        "key": "dUFZQE",
                        "title": "Does your organisation use any other names?",
                        "type": "list",
                        "answer": "",
                    },
                ],
            },
            {
                "question": "About your organisation",
                "fields": [
                    {
                        "key": "vvankL",
                        "title": "What is your organisation's main purpose?",
                        "type": "text",
                        "answer": "",
                    },
                    {
                        "key": "mnXlnA",
                        "title": "Tell us about your organisation's main activities",
                        "type": "text",
                        "answer": "",
                    },
                    {
                        "key": "SULcMg",
                        "title": "Add another activity",
                        "type": "text",
                        "answer": "",
                    },
                    {
                        "key": "CxyfYS",
                        "title": "Have you delivered projects like this before?",
                        "type": "list",
                        "answer": "",
                    },
                ],
            },
            {
                "question": "About your organisation",
                "fields": [
                    {
                        "key": "HQXgYz",
                        "title": "Type of organisation",
                        "type": "other",
                        "answer": "",
                    },
                ],
            },
            {
                "question": "About your organisation",
                "fields": [
                    {
                        "key": "HmuXka",
                        "title": "Type of organisation  (other)",
                        "type": "text",
                        "answer": "",
                    },
                ],
            },
            {
                "question": "About your organisation",
                "fields": [
                    {
                        "key": "Sudpvz",
                        "title": "Which regulatory body is your company registered with?",
                        "type": "list",
                        "answer": "",
                    },
                ],
            },
            {
                "question": "About your organisation",
                "fields": [
                    {
                        "key": "PRDPBF",
                        "title": "Is your organisation a trading subsidiary of a parent company?",
                        "type": "list",
                        "answer": "",
                    },
                ],
            },
            {
                "question": "About your organisation",
                "fields": [
                    {
                        "key": "zjnAVS",
                        "title": "Organisation address",
                        "type": "text",
                        "answer": "",
                    },
                    {
                        "key": "WQbjia",
                        "title": "County",
                        "type": "text",
                        "answer": "",
                    },
                    {
                        "key": "NlIgBS",
                        "title": "Is your correspondence address different to the organisation address?",
                        "type": "list",
                        "answer": "",
                    },
                ],
            },
            {
                "question": "About your organisation",
                "fields": [
                    {
                        "key": "EsVKLG",
                        "title": "Website and social media",
                        "type": "text",
                        "answer": "",
                    },
                ],
            },
        ],
    },
    {
        "status": "NOT_STARTED",
        "form": "project-costs",
        "questions": [
            {
                "question": "Management case",
                "fields": [
                    {
                        "key": "WDDkVB",
                        "title": "Summarise your cash flow for the running of the asset",
                        "type": "text",
                        "answer": "",
                    },
                    {
                        "key": "oaIntA",
                        "title": "If successful, will you use your funding in the next 12 months",
                        "type": "list",
                        "answer": "",
                    },
                ],
            },
        ],
    },
    {
        "status": "NOT_STARTED",
        "form": "project-information",
        "questions": [
            {
                "question": "About your project",
                "fields": [
                    {
                        "key": "RKuzIW",
                        "title": "Have you been given funding through the Community Ownership Fund before?",
                        "type": "list",
                        "answer": "",
                    },
                ],
            },
            {
                "question": "About your project",
                "fields": [
                    {
                        "key": "iktvZS",
                        "title": "Name of previous project",
                        "type": "text",
                        "answer": "",
                    },
                    {
                        "key": "LQcTUZ",
                        "title": "Amount of funding received",
                        "type": "text",
                        "answer": "",
                    },
                ],
            },
            {
                "question": "About your project",
                "fields": [
                    {
                        "key": "uKwRXL",
                        "title": "Project name",
                        "type": "text",
                        "answer": "",
                    },
                    {
                        "key": "BfYLWC",
                        "title": "Tell us how the asset is currently being used, or how it has been used before, and why it's important to the community",
                        "type": "text",
                        "answer": "",
                    },
                    {
                        "key": "KZKFGE",
                        "title": "Explain why the asset is at risk of being lost to the community, or why it has already been lost",
                        "type": "text",
                        "answer": "",
                    },
                    {
                        "key": "efPrAo",
                        "title": "Give a brief summary of your project, including what you hope to achieve",
                        "type": "text",
                        "answer": "",
                    },
                ],
            },
            {
                "question": "About your project",
                "fields": [
                    {
                        "key": "HhXUhD",
                        "title": "Address of the community asset",
                        "type": "text",
                        "answer": "",
                    },
                    {
                        "key": "rmiVDZ",
                        "title": "County",
                        "type": "text",
                        "answer": "",
                    },
                    {
                        "key": "SdZbFW",
                        "title": "In which constituency is your asset?",
                        "type": "text",
                        "answer": "",
                    },
                ],
            },
        ],
    },
    {
        "status": "NOT_STARTED",
        "form": "project-qualification",
        "questions": [
            {
                "question": "Subsidy control / state aid",
                "fields": [
                    {
                        "key": "HvxXPI",
                        "title": "Does your project meet the definition of a subsidy?",
                        "type": "list",
                        "answer": "",
                    },
                ],
            },
        ],
    },
    {
        "status": "NOT_STARTED",
        "form": "risk",
        "questions": [
            {
                "question": "Management case",
                "fields": [
                    {
                        "key": "pwslCf",
                        "title": "Type of risk",
                        "type": "text",
                        "answer": "",
                    },
                    {
                        "key": "tpXXWt",
                        "title": "Describe the risk",
                        "type": "text",
                        "answer": "",
                    },
                    {
                        "key": "fCddUh",
                        "title": "Level of risk",
                        "type": "list",
                        "answer": "",
                    },
                    {
                        "key": "PqVZFh",
                        "title": "Likelihood of risk",
                        "type": "list",
                        "answer": "",
                    },
                    {
                        "key": "BtljVL",
                        "title": "Timeframe of risk",
                        "type": "list",
                        "answer": "",
                    },
                    {
                        "key": "mYRwas",
                        "title": "Mitigation",
                        "type": "text",
                        "answer": "",
                    },
                    {
                        "key": "xGAVRU",
                        "title": "Risk after mitgation",
                        "type": "list",
                        "answer": "",
                    },
                ],
            },
        ],
    },
    {
        "status": "NOT_STARTED",
        "form": "skills-and-resources",
        "questions": [
            {
                "question": "Management case",
                "fields": [
                    {
                        "key": "CBIWnt",
                        "title": "Do you have experience of managing a community asset?",
                        "type": "list",
                        "answer": "",
                    },
                ],
            },
            {
                "question": "Management case",
                "fields": [
                    {
                        "key": "QWveYc",
                        "title": "Describe any experience you have with community assets similar to this",
                        "type": "text",
                        "answer": "",
                    },
                ],
            },
            {
                "question": "Management case",
                "fields": [
                    {
                        "key": "vKnMPG",
                        "title": "Do you have any plans to recruit people to help you manage the asset?",
                        "type": "list",
                        "answer": "",
                    },
                ],
            },
            {
                "question": "Management case",
                "fields": [
                    {
                        "key": "VNjRgZ",
                        "title": "Tell us about the roles you will recruit",
                        "type": "text",
                        "answer": "",
                    },
                ],
            },
        ],
    },
    {
        "status": "NOT_STARTED",
        "form": "value-to-the-community",
        "questions": [
            {
                "question": "Added value to the community",
                "fields": [
                    {
                        "key": "oOPUXI",
                        "title": "Tell us about your local community as a whole",
                        "type": "text",
                        "answer": "",
                    },
                    {
                        "key": "NKOmNL",
                        "title": "Describe any specific challenges your community faces, and how the asset will address these",
                        "type": "text",
                        "answer": "",
                    },
                ],
            },
        ],
    },
    {
        "status": "NOT_STARTED",
        "form": "upload-business-plan",
        "questions": [
            {
                "question": "Management case",
                "fields": [
                ],
            },
        ],
    },
]

    FUND_ROUND_FORMS = {
    "fund-a:spring": COF_R2_FORMS.copy(),
    "fund-b:spring": COF_R2_FORMS.copy(),
    "fund-a:summer": COF_R2_FORMS.copy(),
    "fund-b:summer": COF_R2_FORMS.copy(),
    "funding-service-design:spring": COF_R2_FORMS.copy(),
    "funding-service-design:summer": COF_R2_FORMS.copy(),
    "community-ownership-fund:round-2": COF_R2_FORMS.copy(),
    }