from dataclasses import dataclass
from typing import List

from external_services.models.round import Round


@dataclass
class Fund:
    name: str
    identifier: str
    description: str
    rounds: List[Round] = None

    @staticmethod
    def from_json(data: dict):
        return Fund(
            name=data.get("name"),
            identifier=data.get("id"),
            description=data.get("description"),
        )

    def add_round(self, fund_round: Round):
        if not self.rounds:
            self.rounds = []
        self.rounds.append(fund_round)
