from dataclasses import dataclass
from typing import List
from flask import current_app

from external_services.models.round import Round


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
                name=data.get("fund_name"),
                identifier=data.get("fund_id"),
                description=data.get("fund_description"),
            )
        except AttributeError as e:
            current_app.logger.error("Empty data passed to Fund.from_json")
            raise e

    def add_round(self, fund_round: Round):
        if not self.rounds:
            self.rounds = []
        self.rounds.append(fund_round)
