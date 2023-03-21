from db import db
from db.models import Forms


def add_new_forms(forms, application_id):
    for form in forms:
        new_form_row = Forms(
            application_id=application_id,
            json=[],
            name=form,
            status="NOT_STARTED",
        )
        db.session.add(new_form_row)
        db.session.commit()
    return {"forms": forms}


def get_forms_by_app_id(application_id, as_json=True):
    forms = (
        db.session.query(Forms)
        .filter(Forms.application_id == application_id)
        .all()
    )
    if as_json:
        return [form.as_json() for form in forms]
    else:
        return forms


def get_form(application_id, form_name):
    return (
        db.session.query(Forms)
        .filter(
            Forms.application_id == application_id, Forms.name == form_name
        )
        .one()
    )
