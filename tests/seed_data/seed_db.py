import json

from _helpers import get_blank_forms
from db.models.application import Applications
from db.queries import add_new_forms
from db.queries.application import create_application
from db.queries.application import submit_application
from db.queries.updating.queries import update_form


with open("tests/seed_data/COF_R3W1_all_forms.json", "r") as f:
    COF_R3_W1_FORMS = json.load(f)


def seed_not_started_application(fund_id, round_config, account_id, language):
    return _seed_application(fund_id, round_config["id"], account_id, language)


def seed_in_progress_application(fund_id, round_config, account_id, language):
    app = _seed_application(fund_id, round_config["id"], account_id, language)
    form = [
        form
        for form in COF_R3_W1_FORMS
        if form["name"] == round_config["project_name_form"]
    ][0]
    update_form(
        app.id,
        round_config["project_name_form"],
        form["questions"],
        True,
    )
    return app


def seed_completed_application(fund_id, round_config, account_id, language):
    app = _seed_application(fund_id, round_config["id"], account_id, language)
    for form in COF_R3_W1_FORMS:
        update_form(
            app.id,
            form["name"],
            form["questions"],
            True,
        )
    return app


def seed_submitted_application(fund_id, round_config, account_id, language):
    app = seed_completed_application(fund_id, round_config, account_id, language)
    submit_application(str(app.id))
    return app


def _seed_application(fund_id, round_id, account_id, language) -> Applications:

    app: Applications = create_application(account_id, fund_id, round_id, language)
    empty_forms = get_blank_forms(fund_id, round_id, language)
    add_new_forms(forms=empty_forms, application_id=app.id)
    print(f"Created app with reference {app.reference}")
    return app
