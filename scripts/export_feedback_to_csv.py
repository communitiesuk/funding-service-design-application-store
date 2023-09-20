import jsonpath_rw_ext
import pandas as pd
from db.models import Applications
from db.queries.application.queries import get_applications
from db.schemas.end_of_application_survey import EndOfApplicationSurveyFeedbackSchema
from db.schemas.form import FormsRunnerSchema
from external_services.data import get_application_sections


def get_answer_value(form, search_key, search_value):
    return (
        jsonpath_rw_ext.parse(
            f"$.questions[*].fields[?(@.{search_key} == '{search_value}')]"
        )
        .find(form)[0]
        .value["answer"]
    )


if __name__ == "__main__":
    from app import app  # noqa: E402

    with app.app_context():
        round_id = "6af19a5e-9cae-4f00-9194-cf10d2d7c8a7"
        fund_id = "47aef2f5-3fcb-4d45-acb5-f0152b5f03c4"
        status = "SUBMITTED"

        filters = []
        if fund_id:
            filters.append(Applications.fund_id == fund_id)
        if round_id:
            filters.append(Applications.round_id == round_id)
        if status:
            filters.append(Applications.status == status)

        application_sections = get_application_sections(
            fund_id, round_id, language="en"
        )
        section_names = {}
        for section in application_sections:
            section_names[str(section["id"])] = section["title"]

        applications = get_applications(filters=filters, include_forms=True)
        section_id_list = []

        sections_feedback = []
        total_feedback = []
        serialiser = FormsRunnerSchema()

        for application in applications:
            for form in application.forms:
                form_dict = serialiser.dump(form)
                if "applicant-information" in form.name:
                    applicant_email = get_answer_value(
                        form_dict, "title", "Lead contact email address"
                    )
                if "organisation-information" in form.name:
                    applicant_organisation = get_answer_value(
                        form_dict, "title", "Organisation name"
                    )

            for feedback in application.feedbacks:
                sections_feedback.append(
                    {
                        "application_id": str(application.id),
                        "applicant_email": applicant_email,
                        "applicant_organisation": applicant_organisation,
                        "section": section_names[feedback.section_id],
                        "comment": feedback.feedback_json["comment"],
                        "rating": feedback.feedback_json["rating"],
                    }
                )

            eoas_serialiser = EndOfApplicationSurveyFeedbackSchema()
            eoas = [
                eoas_serialiser.dump(row)
                for row in application.end_of_application_survey
            ]
            total_feedback.append(
                {
                    "application_id": str(application.id),
                    "applicant_email": applicant_email,
                    "applicant_organisation": applicant_organisation,
                    "overall_application_experience": eoas[0]["data"][
                        "overall_application_experience"
                    ],
                    "more_detail": eoas[0]["data"]["more_detail"],
                    "demonstrate_why_org_funding": eoas[1]["data"][
                        "demonstrate_why_org_funding"
                    ],
                    "understand_eligibility_criteria": eoas[2]["data"][
                        "understand_eligibility_criteria"
                    ],
                    "hours_spent": eoas[3]["data"]["hours_spent"],
                }
            )

        writer = pd.ExcelWriter("fsd.xlsx")
        df1 = pd.DataFrame(sections_feedback)
        df2 = pd.DataFrame(total_feedback)
        df1.to_excel(writer, sheet_name="section_feedback")
        df2.to_excel(writer, sheet_name="end_of_application_survey")
        writer.close()

        print(sections_feedback)
