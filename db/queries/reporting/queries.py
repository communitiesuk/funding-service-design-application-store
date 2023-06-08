import csv
import io
import re
from typing import Iterable
from typing import Optional

from db.models import Applications
from db.queries import get_applications
from db.queries.application import get_count_by_status


def export_json_to_csv(return_data, headers=None):
    output = io.StringIO()
    if type(return_data) == list:
        if not headers:
            headers = return_data[0].keys()
        w = csv.DictWriter(output, headers)
        w.writeheader()
        w.writerows(return_data)
    else:
        w = csv.DictWriter(output, return_data.keys())
        w.writeheader()
        w.writerow(return_data)
    bytes_object = bytes(output.getvalue(), encoding="utf-8")
    bytes_output = io.BytesIO(bytes_object)
    return bytes_output


def get_general_status_applications_report(
    round_id: Optional[str] = None, fund_id: Optional[str] = None
):
    return get_count_by_status(round_id, fund_id)


KEY_REPORT_MAPPING = [
    {
        "form_name": "organisation-information",
        "form_name_cy": "gwybodaeth-am-y-sefydliad",
        "key": "WWWWxy",
        "return_field": "eoi_reference",
    },
    {
        "form_name": "organisation-information",
        "form_name_cy": "gwybodaeth-am-y-sefydliad",
        "key": "YdtlQZ",
        "return_field": "organisation_name",
    },
    {
        "form_name": "organisation-information",
        "form_name_cy": "gwybodaeth-am-y-sefydliad",
        "key": "lajFtB",
        "return_field": "organisation_type",
    },
    {
        "form_name": "asset-information",
        "form_name_cy": "gwybodaeth-am-yr-ased",
        "key": "yaQoxU",
        "return_field": "asset_type",
    },
    {
        "form_name": "project-information",
        "form_name_cy": "gwybodaeth-am-y-prosiect",
        "key": "yEmHpp",
        "return_field": "geography",
    },
    {
        "form_name": "funding-required",
        "form_name_cy": "cyllid-sydd-ei-angen",
        "key": "JzWvhj",
        "return_field": "capital",
    },
    {
        "form_name": "funding-required",
        "form_name_cy": "cyllid-sydd-ei-angen",
        "key": "jLIgoi",
        "return_field": "revenue",
    },
    {
        "form_name": "organisation-information-ns",
        "key": "opFJRm",
        "return_field": "organisation_name_nstf",
    },
]


def get_key_report_field_headers(
    mapping: Iterable[dict] = KEY_REPORT_MAPPING,
) -> Iterable[str]:
    return [field["return_field"] for field in KEY_REPORT_MAPPING]


def get_report_for_applications(
    *,  # kwargs only
    status: Optional[str] = None,
    application_ids: Optional[list[str]] = None,
    round_id: Optional[str] = None,
    fund_id: Optional[str] = None,
):
    filters = []
    if status:
        filters.append(Applications.status == status)
    if application_ids:
        filters.append(Applications.id.in_(application_ids))
    if fund_id:
        filters.append(Applications.fund_id == fund_id)
    if round_id:
        filters.append(Applications.round_id == round_id)
    applications = get_applications(
        filters=filters,
        include_forms=True,
        as_json=True,
    )

    return_json_list = []
    for application in applications:
        return_json = {field: None for field in get_key_report_field_headers()}

        report_config_forms = [
            report_config.get("form_name_cy")
            if application["language"] == "cy"
            else report_config.get("form_name")
            for report_config in KEY_REPORT_MAPPING
        ]

        report_config_keys = [
            report_config.get("key") for report_config in KEY_REPORT_MAPPING
        ]

        for application_form in application["forms"]:
            # does form exist in form reporting config
            if application_form.get("name") in report_config_forms:
                for question in application_form["questions"]:
                    # does forms field_id exist in
                    # form reporting config
                    for field in question["fields"]:
                        if field.get("key") in report_config_keys:
                            return_field = [
                                report_config.get("return_field")
                                for report_config in KEY_REPORT_MAPPING
                                if report_config.get("key") == field.get("key")
                            ][0]
                            if field.get("key") == "yEmHpp" and field.get("answer"):
                                postcode = re.search(
                                    "([A-Za-z][A-Ha-hJ-Yj-y]?[0-9][A-Za-z0-9]?"
                                    " ?[0-9][A-Za-z]{2}|[Gg][Ii][Rr]"
                                    " ?0[Aa]{2})",  # noqa
                                    field.get("answer"),
                                )
                                return_json[return_field] = postcode.group()
                            else:
                                return_json[return_field] = field.get("answer")
        return_json_list.append(return_json)
    return return_json_list
