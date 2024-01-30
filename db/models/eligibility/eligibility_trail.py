from uuid import uuid4

from db import db
from flask_sqlalchemy.model import DefaultMeta
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func


BaseModel: DefaultMeta = db.Model


class EligibilityUpdate(BaseModel):
    id = Column("id", UUID(as_uuid=True), default=uuid4, primary_key=True)
    date_created = Column("date_created", db.DateTime(), server_default=func.now())
    eligible = Column("eligible", db.Boolean())
