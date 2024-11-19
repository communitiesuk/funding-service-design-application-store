from dataclasses import dataclass
from typing import Optional

from flask import current_app

from external_services.models.round import Round


@dataclass
class Fund:
    name: str
    identifier: str
    short_name: str
    description: str
    welsh_available: bool
    name_json: str
    rounds: Optional[list[Round]] = None

    @staticmethod
    def from_json(data: dict):
        try:
            return Fund(
                name=data["name"],
                identifier=data["id"],
                short_name=data["short_name"],
                description=data["description"],
                welsh_available=data["welsh_available"],
                name_json=data["name_json"],
            )
        except AttributeError as e:
            current_app.logger.error("Empty data passed to Fund.from_json")
            raise e

    def add_round(self, fund_round: Round) -> None:
        if not self.rounds:
            self.rounds = []
        self.rounds.append(fund_round)
