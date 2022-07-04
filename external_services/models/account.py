from dataclasses import dataclass
from typing import List

from config import Config
from external_services.data import get_data

ACCOUNT_STORE_API_HOST = Config.ACCOUNT_STORE_API_HOST
ACCOUNTS_ENDPOINT = Config.ACCOUNTS_ENDPOINT


@dataclass
class Account(object):
    id: str
    email: str
    applications: List

    @staticmethod
    def from_json(data: dict):
        return Account(
            id=data.get("account_id"),
            email=data.get("email_address"),
            applications=data.get("applications"),
        )


class AccountError(Exception):
    """Exception raised for errors in Account management

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message="Sorry, there was a problem, please try later"):
        self.message = message
        super().__init__(self.message)


class AccountMethods(Account):
    @staticmethod
    def get_account(
        email: str = None, account_id: str = None
    ) -> Account | None:
        """
        Get an account from the account store using either
        an email address or account_id.

        Args:
            email (str, optional): The account email address
            Defaults to None.
            account_id (str, optional): The account id. Defaults to None.

        Raises:
            TypeError: If both an email address or account id is given,
            a TypeError is raised.

        Returns:
            Account object or None
        """
        if email is account_id is None:
            raise TypeError("Requires an email address or account_id")

        url = Config.ACCOUNT_STORE_API_HOST + Config.ACCOUNTS_ENDPOINT
        params = {"email_address": email, "account_id": account_id}
        response = get_data(url, params)

        if response and "account_id" in response:
            return Account.from_json(response)
