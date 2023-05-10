from external_services import get_application_sections


def get_form_name(section):
    forms = set()
    if section["children"]:
        for child in section["children"]:
            forms.update(get_form_name(child))
    if section["form_name"]:
        forms.add(section["form_name"])
    return forms


def get_forms_from_sections(sections, language=None):
    mint_form_list = set()
    for section in sections:
        mint_form_list.update(get_form_name(section))
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
    application_sections = get_application_sections(fund_id, round_id)
    if application_sections:
        forms = get_forms_from_sections(application_sections)
        if not forms:
            raise Exception(f"Could not find forms for {fund_id} - {round_id}")
        return forms
    raise Exception(
        f"Could not find fund round for {fund_id} - {round_id}  in fund store."
    )
