import csv
import io

from db.queries import get_application
from db.queries.application import get_all_applications
from db.queries.application import get_count_by_status


def export_json_to_csv(return_data):
    output = io.StringIO()
    if type(return_data) == list:
        headers = return_data[0]
        w = csv.DictWriter(output, headers.keys())
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


def get_report_for_all_applications(application_id=None):
    """

    :param application_id: generate report for only this application ID
    (if not specified all applications are queried)
    :return: list of dict
    """
    if application_id:
        applications = [get_application(application_id)]
    else:
        applications = get_all_applications()

    return_json_list = []
    for application in applications:
        return_json = {
            "application_id": application.as_dict().get("id"),
            "asset_type": None,
            "capital": None,
            "geography": None,
            "organisation_type": None,
            "revenue": None,
        }
        stored_forms = [form.as_json() for form in application.forms]
        list_of_forms = [
            {
                "form_name": "organisation-information",
                "key": "lajFtB",
                "title": "Type of Organisation",
                "return_field": "organisation_type",
            },
            {
                "form_name": "asset-information",
                "key": "yaQoxU",
                "title": "Asset Type",
                "return_field": "asset_type",
            },
            {
                "form_name": "project-information",
                "key": "yEmHpp",
                "title": "Address of the community asset",
                "return_field": "geography",
            },
            {
                "form_name": "funding-required",
                "key": "MultiInputField",
                "title": "Capital costs",
                "return_field": "capital",
            },
            {
                "form_name": "funding-required",
                "key": "MultiInputField-2",
                "title": "Revenue costs",
                "return_field": "revenue",
            },
        ]
        for form in stored_forms:
            if form.get("name") in [
                form.get("form_name") for form in list_of_forms
            ]:
                for question in form["questions"]:
                    for field in question["fields"]:
                        if field.get("key") in [
                            form.get("key") for form in list_of_forms
                        ]:
                            return_field = [
                                form.get("return_field")
                                for form in list_of_forms
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
