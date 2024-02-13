from dataclasses import dataclass


@dataclass
class Account:
    id: str
    email: str
    full_name: str

    @staticmethod
    def from_json(data: dict):
        return Account(id=data["account_id"], email=data["email_address"], full_name=data.get("full_name", ""))
