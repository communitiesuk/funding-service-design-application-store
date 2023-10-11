import csv
import io
from typing import Any
from typing import Optional

import pandas as pd
from config.key_report_mappings.mappings import ROUND_ID_TO_KEY_REPORT_MAPPING
from config.key_report_mappings.model import ApplicationColumnMappingItem
from config.key_report_mappings.model import FormMappingItem
from config.key_report_mappings.model import MappingItem
from db.models import Applications
from db.queries import get_applications
from db.queries.application import get_count_by_status

APPLICATION_STATUS_HEADERS = [
    "fund_id",
    "round_id",
    "NOT_STARTED",
    "IN_PROGRESS",
    "COMPLETED",
    "SUBMITTED",
]


def export_application_statuses_to_csv(return_data):
    output = io.StringIO()

    w = csv.DictWriter(output, APPLICATION_STATUS_HEADERS)
    w.writeheader()
    for fund in return_data:
        fund_id = fund["fund_id"]
        for round in fund["rounds"]:
            round_id = round["round_id"]
            w.writerow(
                {
                    "fund_id": fund_id,
                    "round_id": round_id,
                    **round["application_statuses"],
                }
            )

    bytes_object = bytes(output.getvalue(), encoding="utf-8")
    bytes_output = io.BytesIO(bytes_object)
    return bytes_output


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


def export_json_to_excel(return_data: dict):
    output = io.BytesIO()

    if not return_data:
        return output

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        for key in return_data.keys():
            df = pd.DataFrame(return_data[key])
            df.to_excel(writer, sheet_name=key)

    # seeking is necessary
    output.seek(0)
    return output


def get_general_status_applications_report(
    round_id: Optional[str] = None, fund_id: Optional[str] = None
):
    return get_count_by_status(round_id, fund_id)


def get_key_report_field_headers(round_id: str) -> list[str]:
    mapping: list[MappingItem] = ROUND_ID_TO_KEY_REPORT_MAPPING[round_id]
    return [field.return_field for field in mapping]


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

    return_json_list: list[dict[str, Any]] = []
    mapping: list[MappingItem] = ROUND_ID_TO_KEY_REPORT_MAPPING[round_id]
    for application in applications:
        return_json = map_application_key_fields(application, mapping, round_id)
        return_json_list.append(return_json)
    return return_json_list


def map_application_key_fields(
    application: dict[str, Any], mapping: list[MappingItem], round_id: str
) -> dict[str, Any]:
    return_json: dict[str, Any] = {
        field: None for field in get_key_report_field_headers(round_id)
    }
    language: str = application["language"]

    form_mapping_items = [item for item in mapping if isinstance(item, FormMappingItem)]
    report_config_forms: list[str] = [
        report_config.get_form_name(language) for report_config in form_mapping_items
    ]
    report_config_keys: list[str] = [
        report_config.key for report_config in form_mapping_items
    ]

    form_mapping_items = [item for item in mapping if isinstance(item, FormMappingItem)]
    for application_form in application["forms"]:
        # skip any forms that are not in the report config
        if application_form.get("name") not in report_config_forms:
            continue

        for field in (f for q in application_form["questions"] for f in q["fields"]):
            # skip any fields that are not in the report config
            if field.get("key") not in report_config_keys:
                continue

            for mapping_item in form_mapping_items:
                if mapping_item.key == field.get("key"):
                    return_json[mapping_item.return_field] = mapping_item.format_answer(
                        field
                    )

    application_column_mapping_items = [
        item for item in mapping if isinstance(item, ApplicationColumnMappingItem)
    ]
    for mapping_item in application_column_mapping_items:
        return_json[mapping_item.return_field] = mapping_item.format_answer(
            application.get(mapping_item.column_name)
        )

    return_fields_ordered = [item.return_field for item in mapping]
    sorted_result_json = {k: return_json.get(k) for k in return_fields_ordered}

    return sorted_result_json
