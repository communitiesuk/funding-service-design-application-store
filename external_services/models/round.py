from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass
class Round:
    title: str
    identifier: str
    fund_id: str
    opens: datetime
    deadline: datetime
    assessment_deadline: datetime
    assessment_criteria_weighting: List[dict]

    @staticmethod
    def from_json(data: dict):
        return Round(
            title=data.get("title"),
            identifier=data.get("id"),
            fund_id=data.get("fund_id"),
            opens=data.get("opens"),
            deadline=data.get("deadline"),
            assessment_deadline=data.get("assessment_deadline"),
            assessment_criteria_weighting=data.get(
                "assessment_criteria_weighting"
            ),
        )
