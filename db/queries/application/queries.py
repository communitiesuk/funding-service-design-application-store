from db.models import Applications
from db.models import Forms
from db import db
from sqlalchemy.orm import joinedload


def get_application(app_id, include_forms=False):

    joined_rows = db.session.query(Applications).options(joinedLoad(Applications.forms._and(Forms.id == app_id))).filter(Applications.id == app_id).all()

    return [row._as_dict() for row in joined_rows]

