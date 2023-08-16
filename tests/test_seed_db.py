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


@pytest.fixture
def local_fund_store():
    # Update config to point at local fund store for retrieving application config (eg. forms)
    Config.FUND_STORE_API_HOST = "http://localhost:3001"


# @pytest.mark.skip(reason="Needs running fund-store")
def test_seed_application_not_started(_db, clear_test_data, local_fund_store):
    seeded_app = seed_not_started_application(COF["id"], R3W1, uuid4(), LANG_EN)
    assert seeded_app
    status_result = get_application_status(seeded_app.id)
    assert status_result == Status.NOT_STARTED


# @pytest.mark.skip(reason="Needs running fund-store")
def test_seed_application_in_progress(_db, clear_test_data, local_fund_store):
    seeded_app = seed_in_progress_application(COF["id"], R3W1, uuid4(), LANG_EN)
    assert seeded_app
    status_result = get_application_status(seeded_app.id)
    assert status_result == Status.IN_PROGRESS


# @pytest.mark.skip(reason="Needs running fund-store")
def test_seed_application_completed(_db, clear_test_data, local_fund_store):
    seeded_app = seed_completed_application(COF["id"], R3W1, uuid4(), LANG_EN)
    assert seeded_app
    status_result = get_application_status(seeded_app.id)
    assert status_result == Status.COMPLETED


# @pytest.mark.skip(reason="Needs running fund-store")
def test_seed_application_submitted(_db, clear_test_data, local_fund_store, mocker):
    mocker.patch(
        "db.queries.application.queries.list_files_by_prefix", return_value=MagicMock()
    )
    seeded_app = seed_submitted_application(COF["id"], R3W1, uuid4(), LANG_EN)
    assert seeded_app
    status_result = get_application_status(seeded_app.id)
    assert status_result == Status.SUBMITTED


@pytest.mark.skip(reason="Not a test")
def test_retrieve_test_data(app):
    target_app = "8a4a5f36-4e52-4d75-919a-e64f446a3f99"
    with app.app_context():
        forms = get_forms_by_app_id(target_app, as_json=True)

    with open("forms.json", "w") as f:
        f.write(json.dumps(forms))
