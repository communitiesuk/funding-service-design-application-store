from dataclasses import dataclass


@dataclass
class Account():
    id: str
    email: str

    @staticmethod
    def from_json(data: dict):
        return Account(
            id=data["account_id"],
            email=data["email_address"]
        )
