from dataclasses import dataclass
from datetime import datetime


@dataclass
class Round:
    title: str
    identifier: str
    fund_id: str
    opens: datetime
    deadline: datetime
    assessment_deadline: datetime
    assessment_criteria_weighting: dict

    @staticmethod
    def from_json(data: dict):
        assessment_criteria_weighting = []
        return Round(
            title=data.get("title"),
            identifier=data.get("id"),
            fund_id=data.get("fund_id"),
            opens=data.get("opens"),
            deadline=data.get("deadline"),
            assessment_deadline=data.get("deadline"),
            assessment_criteria_weighting=assessment_criteria_weighting,
        )

    def add_eligibility_criteria(self, key: str, value: object):
        self.eligibility_criteria.update({key: value})
