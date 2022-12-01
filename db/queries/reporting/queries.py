import csv
import io
from db.models.application.enums import Status

from db.queries import get_application
from db.queries.application import get_all_applications
from db.queries.application import get_count_by_status
from db.queries import get_application, get_applications
from db.models import Applications


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


def get_report_for_application(application_id):
    return get_report_for_all_applications(application_id)


def get_general_status_applications_report():
    return get_count_by_status()


KEY_REPORT_MAPPING = [
    {
        "form_name": "organisation-information",
        "key": "WWWWxy",
        "return_field": "eoi_reference",
    },
    {
        "form_name": "organisation-information",
        "key": "YdtlQZ",
        "return_field": "organisation_name",
    },
    {
        "form_name": "organisation-information",
        "key": "lajFtB",
        "return_field": "organisation_type",
    },
    {
        "form_name": "asset-information",
        "key": "yaQoxU",
        "return_field": "asset_type",
    },
    {
        "form_name": "project-information",
        "key": "yEmHpp",
        "return_field": "geography",
    },
    {
        "form_name": "funding-required",
        "key": "JzWvhj",
        "return_field": "capital",
    },
    {
        "form_name": "funding-required",
        "key": "jLIgoi",
        "return_field": "revenue",
    },
]


def get_key_report_field_headers(
    mapping: Iterable[dict] = KEY_REPORT_MAPPING,
) -> Iterable[str]:
    return [field["return_field"] for field in KEY_REPORT_MAPPING]


def get_report_for_all_applications(
    application_id=None,
):
    """

    :param application_id: generate report for only this application ID
    (if not specified all applications are queried)
    :return: list of dict
    """
    if application_id:
        applications = [
            get_application(application_id, include_forms=True, as_json=True)
        ]
    else:
        applications = get_applications(filters=[Applications.status == Status.SUBMITTED], include_forms=True, as_json=True)

    return_json_list = []
    return_json = {field: None for field in get_key_report_field_headers()}

    for form in applications.forms:
        if form.get("name") in [
            form.get("form_name") for form in KEY_REPORT_MAPPING
        ]:
            for question in form["questions"]:
                for field in question["fields"]:
                    if field.get("key") in [
                        form.get("key") for form in KEY_REPORT_MAPPING
                    ]:
                        return_field = [
                            form.get("return_field")
                            for form in KEY_REPORT_MAPPING
                            if form.get("key") == field.get("key")
                        ][0]
                        if field.get("key") == "yEmHpp" and field.get(
                            "answer"
                        ):
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