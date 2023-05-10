from config import Config
from external_services import get_fund
from external_services import get_round


def get_forms_from_form_config(form_config, fund_id, round_id, language):
    mint_form_list = set()
    forms_config = form_config.get(":".join([fund_id, round_id]))
    for form_config in forms_config:
        for form in form_config["ordered_form_names_within_section"]:
            mint_form_list.add(form[language])
    return mint_form_list


def get_blank_forms(fund_id: str, round_id: str, language: str):
    """
    Get the list of forms required to populate a blank
    application for a fund round

    Args:
        fund_id: (str) The id of the fund
        round_id: (str) The id of the fund round

    Returns:
        A list of json forms to populate the form
    """
    fund = get_fund(fund_id)
    fund_round = get_round(fund_id, round_id)
    if fund and fund_round:
        form_config = Config.FORMS_CONFIG_FOR_FUND_ROUND
        forms = get_forms_from_form_config(form_config, fund_id, round_id, language)
        if not forms:
            raise Exception(f"Could not find forms for {fund_id} - {round_id}")
        return forms.copy()
    raise Exception(
        f"Could not find fund round for {fund_id} - {round_id}  in fund store."
    )
