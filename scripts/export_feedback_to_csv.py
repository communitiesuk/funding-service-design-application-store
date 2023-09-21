import pandas as pd
from db.queries.feedback import retrieve_all_feedbacks_and_surveys


if __name__ == "__main__":
    from app import app  # noqa: E402

    with app.app_context():
        round_id = "6af19a5e-9cae-4f00-9194-cf10d2d7c8a7"
        fund_id = "47aef2f5-3fcb-4d45-acb5-f0152b5f03c4"
        status = "SUBMITTED"
        data = retrieve_all_feedbacks_and_surveys(fund_id, round_id, status)
        print(data)

        writer = pd.ExcelWriter("fsd.xlsx")
        df1 = pd.DataFrame(data["sections_feedback"])
        df2 = pd.DataFrame(data["end_of_application_survey_data"])
        df1.to_excel(writer, sheet_name="section_feedback")
        df2.to_excel(writer, sheet_name="end_of_application_survey")
        writer.close()
