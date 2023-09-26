from dataclasses import dataclass
from typing import Optional


@dataclass
class Round:
    id: str
    assessment_deadline: str
    deadline: str
    fund_id: str
    opens: str
    title: str
    short_name: str
    contact_email: str
    requires_feedback: bool = False
    project_name_field_id: Optional[str] = None
    mark_as_complete_enabled: bool = False

    @staticmethod
    def from_json(data: dict):
        return Round(
            title=data["title"],
            id=data["id"],
            fund_id=data["fund_id"],
            short_name=data["short_name"],
            opens=data["opens"],
            deadline=data["deadline"],
            assessment_deadline=data["assessment_deadline"],
            project_name_field_id=data.get("project_name_field_id", None),
            contact_email=data.get("contact_email", None),
            requires_feedback=data.get("requires_feedback") or False,
            mark_as_complete_enabled=data.get("mark_as_complete_enabled") or False,
        )
