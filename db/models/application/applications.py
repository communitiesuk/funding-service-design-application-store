import uuid

from db import db
from db.models.application.enums import Language
from db.models.application.enums import Status
from flask_sqlalchemy.model import DefaultMeta
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


BaseModel: DefaultMeta = db.Model


class Applications(BaseModel):
    id = Column(
        "id",
        UUID(as_uuid=True),
        default=uuid.uuid4,
        primary_key=True,
        nullable=False,
    )
    account_id = Column("account_id", db.String(), nullable=False)
    fund_id = Column("fund_id", db.String(), nullable=False)
    round_id = Column("round_id", db.String(), nullable=False)
    key = Column("key", db.String(), nullable=False)
    language = Column("language", ENUM(Language), nullable=True)
    reference = Column("reference", db.String(), nullable=False, unique=True)
    project_name = Column(
        "project_name",
        db.String(),
        nullable=True,
    )
    started_at = Column("started_at", DateTime(), server_default=func.now())
    status = Column("status", ENUM(Status), default="NOT_STARTED", nullable=False)
    date_submitted = Column("date_submitted", DateTime())
    last_edited = Column("last_edited", DateTime(), server_default=func.now())
    forms = relationship("Forms")
    feedbacks = relationship("Feedback")
    end_of_application_survey = relationship("EndOfApplicationSurveyFeedback")

    __table_args__ = (
        db.UniqueConstraint("fund_id", "round_id", "key", name="_reference"),
    )

    def as_dict(self):
        date_submitted = (
            self.date_submitted.isoformat() if self.date_submitted else "null"
        )
        return {
            "id": str(self.id),
            "account_id": self.account_id,
            "round_id": self.round_id,
            "fund_id": self.fund_id,
            "language": self.language.name if self.language else "en",
            "reference": self.reference,
            "project_name": self.project_name or None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "status": self.status.name if self.status else None,
            "last_edited": self.last_edited.isoformat()
            if self.last_edited
            else (self.started_at.isoformat() if self.started_at else None),
            "date_submitted": date_submitted,
        }
