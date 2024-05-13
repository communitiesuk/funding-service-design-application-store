import json
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from config import Config
from db.models.application.applications import Status
from db.queries.application import get_application_status
from db.queries.form import get_forms_by_app_id
from scripts.seed_db_test_data import FUND_CONFIG
from tests.seed_data.seed_db import seed_completed_application
from tests.seed_data.seed_db import seed_in_progress_application
from tests.seed_data.seed_db import seed_not_started_application
from tests.seed_data.seed_db import seed_submitted_application


LANG_EN = "en"
COF = FUND_CONFIG["COF"]
R3W1 = COF["rounds"]["R3W1"]
NSTF = FUND_CONFIG["NSTF"]
R2 = NSTF["rounds"]["R2"]
HSRA = FUND_CONFIG["HSRA"]
R1 = HSRA["rounds"]["R1"]


@pytest.fixture
def local_fund_store():
    # Update config to point at local fund store for retrieving application config (eg. forms)
    Config.FUND_STORE_API_HOST = "http://localhost:3001"


@pytest.mark.skip(reason="Needs running fund-store")
@pytest.mark.parametrize("fund_config, round_config", [(COF, R3W1), (NSTF, R2)])
def test_seed_application_not_started(fund_config, round_config, _db, clear_test_data, local_fund_store):
    seeded_app = seed_not_started_application(fund_config, round_config, uuid4(), LANG_EN)
    assert seeded_app
    status_result = get_application_status(seeded_app.id)
    assert status_result == Status.NOT_STARTED


@pytest.mark.skip(reason="Needs running fund-store")
@pytest.mark.parametrize("fund_config, round_config", [(COF, R3W1), (NSTF, R2)])
def test_seed_application_in_progress(fund_config, round_config, _db, clear_test_data, local_fund_store):
    seeded_app = seed_in_progress_application(fund_config, round_config, uuid4(), LANG_EN)
    assert seeded_app
    status_result = get_application_status(seeded_app.id)
    assert status_result == Status.IN_PROGRESS


@pytest.mark.skip(reason="Needs running fund-store")
@pytest.mark.parametrize("fund_config, round_config", [(COF, R3W1), (NSTF, R2)])
def test_seed_application_completed(fund_config, round_config, _db, clear_test_data, local_fund_store):
    seeded_app = seed_completed_application(fund_config, round_config, uuid4(), LANG_EN)
    assert seeded_app
    status_result = get_application_status(seeded_app.id)
    assert status_result == Status.COMPLETED


# @pytest.mark.skip(reason="Needs running fund-store")
@pytest.mark.parametrize("fund_config, round_config", [(HSRA, R1)])
def test_seed_application_submitted(fund_config, round_config, _db, clear_test_data, local_fund_store, mocker):
    mocker.patch("db.queries.application.queries.list_files_by_prefix", return_value=MagicMock())
    seeded_app = seed_submitted_application(fund_config, round_config, uuid4(), LANG_EN)
    assert seeded_app
    status_result = get_application_status(seeded_app.id)
    assert status_result == Status.SUBMITTED


# @pytest.mark.skip(reason="Not a test")
def test_retrieve_test_data(app):
    target_app = "b1920085-c29b-443f-870a-639455022210"
    with app.app_context():
        forms = get_forms_by_app_id(target_app, as_json=True)

    with open("forms.json", "w") as f:
        f.write(json.dumps(forms))
