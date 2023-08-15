from uuid import uuid4

import pytest
from db.models.application.applications import Status
from db.queries.application import get_application_status
from fsd_test_utils.test_config.useful_config import UsefulConfig
from tests.seed_data.seed_db import seed_in_progress_application
from tests.seed_data.seed_db import seed_not_started_application


LANG_EN = "en"


@pytest.mark.skip(reason="Needs running fund-store")
def test_seed_application_not_started(_db, clear_test_data):
    seeded_app = seed_not_started_application(
        UsefulConfig.COF_FUND_ID, UsefulConfig.COF_ROUND_3_W1_ID, uuid4(), LANG_EN
    )
    assert seeded_app
    status_result = get_application_status(seeded_app.id)
    assert status_result == Status.NOT_STARTED


@pytest.mark.skip(reason="Needs running fund-store")
def test_seed_application_in_progress(_db, clear_test_data):
    seeded_app = seed_in_progress_application(
        UsefulConfig.COF_FUND_ID, UsefulConfig.COF_ROUND_3_W1_ID, uuid4(), LANG_EN
    )
    assert seeded_app
    status_result = get_application_status(seeded_app.id)
    assert status_result == Status.IN_PROGRESS
