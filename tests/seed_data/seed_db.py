from _helpers import get_blank_forms
from db.models.application import Applications
from db.queries import add_new_forms
from db.queries.application import create_application
from db.queries.updating.queries import update_form
from tests.seed_data.data import COF_R3W1_PROJECT_INFO_FORM_NAME
from tests.seed_data.data import COF_R3W1_PROJECT_INFO_QUESTION_JSON


def seed_not_started_application(fund_id, round_id, account_id, language):
    return _seed_application(fund_id, round_id, account_id, language)


def seed_in_progress_application(fund_id, round_id, account_id, language):
    app = _seed_application(fund_id, round_id, account_id, language)
    update_form(
        app.id,
        COF_R3W1_PROJECT_INFO_FORM_NAME,
        COF_R3W1_PROJECT_INFO_QUESTION_JSON,
        False,
    )
    return app


def _seed_application(fund_id, round_id, account_id, language) -> Applications:

    # Update config to point at local fund store for retrieving application config (eg. forms)
    # Config.FUND_STORE_API_HOST = "http://localhost:3001"

    app: Applications = create_application(account_id, fund_id, round_id, language)
    empty_forms = get_blank_forms(fund_id, round_id, language)
    add_new_forms(forms=empty_forms, application_id=app.id)
    print(f"Created app with reference {app.reference}")
    return app
