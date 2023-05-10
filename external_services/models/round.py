from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass
class Round:
    title: str
    identifier: str
    fund_id: str
    short_name: str
    opens: datetime
    deadline: datetime
    assessment_deadline: datetime
    assessment_criteria_weighting: List[dict]

    @staticmethod
    def from_json(data: dict):
        return Round(
            title=data["title"],
            identifier=data["id"],
            fund_id=data["fund_id"],
            short_name=data["short_name"],
            opens=data["opens"],
            deadline=data["deadline"],
            assessment_deadline=data["assessment_deadline"],
            assessment_criteria_weighting=data["assessment_criteria_weighting"],
        )
