import datetime
import uuid
from operator import itemgetter
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
            fund_round_forms = Config.FUND_ROUND_FORMS
            forms = fund_round_forms.get(":".join([fund_id, round_id]))
            if not forms:
                raise Exception(
                    f"Could not find form sections for {fund_id} - {round_id}"
                )
            return forms.copy()
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
