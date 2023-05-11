from dataclasses import dataclass


@dataclass
class Round:
    id: str
    assessment_deadline: str
    deadline: str
    fund_id: str
    opens: str
    title: str
    short_name: str

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
        )
