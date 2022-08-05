import datetime
import uuid
from operator import itemgetter
from typing import List
from db.models.applications import Applications
from db.models.forms import Forms, SectionsMethods
from db import db
from os import getenv
from database.initial_data import initial_application_store_state
from dateutil import parser as date_parser
from dateutil.tz import UTC
from external_services.data import get_fund
from external_services.data import get_round
from external_services.models.account import AccountMethods
from external_services.models.notification import Notification
from config import Config

class ApplicationHelpers:
    @staticmethod
    def get_blank_sections(fund_id: str, round_id: str):
        """
        Get the list of sections required to populate a blank
        application for a fund round

        Args:
            fund_id: (str) The id of the fund
            round_id: (str) The id of the fund round

        Returns:
            A list of json sections to populate the form
        """
        fund = get_fund(fund_id)
        fund_round = get_round(fund_id, round_id)
        if fund and fund_round:
            fund_round_sections = Config.FUND_ROUND_SECTIONS
            sections = fund_round_sections.get(":".join([fund_id, round_id]))
            if not sections:
                raise Exception(
                    f"Could not find form sections for {fund_id} - {round_id}"
                )
            return sections.copy()
        raise Exception(f"Could not find fund round for {fund_id} - {round_id}")


    def order_applications(applications, order_by, order_rev):
        """
        Returns a list of ordered applications
        """
        ordered_applications = []
        if order_by and order_by in [
            "id",
            "status",
            "account_id",
            "assessment_deadline",
            "started_at"
        ]:
            ordered_applications = sorted(
                applications,
                key=itemgetter(order_by),
                reverse=order_rev,
            )

        return ordered_applications
