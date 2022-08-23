from dataclasses import dataclass
from typing import List

from external_services.models.round import Round
from flask import current_app


@dataclass
class Fund:
    name: str
    identifier: str
    description: str
    rounds: List[Round] = None

    @staticmethod
    def from_json(data: dict):
        try:
            return Fund(
                name=data.get("name"),
                identifier=data.get("id"),
                description=data.get("description"),
            )
        except AttributeError as e:
            current_app.logger.error("Empty data passed to Fund.from_json")
            raise e

    def add_round(self, fund_round: Round):
        if not self.rounds:
            self.rounds = []
        self.rounds.append(fund_round)
