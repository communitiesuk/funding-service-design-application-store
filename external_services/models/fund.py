from dataclasses import dataclass
from typing import List, Optional, Self

from external_services.models.round import Round
from flask import current_app


@dataclass
class Fund:
    name: str
    identifier: str
    short_name: str
    description: str
    rounds: Optional[List[Round]] = None

    @staticmethod
    def from_json(data: dict) -> Self:
        try:
            return Fund(
                name=data["name"],
                identifier=data["id"],
                short_name=data["short_name"],
                description=data["description"],
            )
        except AttributeError as e:
            current_app.logger.error("Empty data passed to Fund.from_json")
            raise e

    def add_round(self, fund_round: Round) -> None:
        if not self.rounds:
            self.rounds = []
        self.rounds.append(fund_round)
