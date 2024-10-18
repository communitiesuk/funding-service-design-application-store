from fsd_utils import NotifyConstants

expected_application_json = {
    NotifyConstants.FIELD_TYPE: NotifyConstants.TEMPLATE_TYPE_APPLICATION,
    NotifyConstants.FIELD_TO: "test_application@example.com",
    NotifyConstants.FIELD_CONTENT: {
        NotifyConstants.MAGIC_LINK_CONTACT_HELP_EMAIL_FIELD: "COF@communities.gov.uk",
        NotifyConstants.APPLICATION_FIELD: {
            "id": "123456789",
            "reference": "1564564564-56-4-54-4654",
            "fund_id": "47aef2f5-3fcb-4d45-acb5-f0152b5f03c4",
            "round_name": "summer",
            "date_submitted": "2022-05-14T09:25:44.124542",
            "fund_name": "Community Ownership Fund",
            "language": "en",
            NotifyConstants.APPLICATION_FORMS_FIELD: [
                {
                    NotifyConstants.APPLICATION_NAME_FIELD: "about-your-org",
                    NotifyConstants.APPLICATION_QUESTIONS_FIELD: [
                        {
                            "question": "Application information",
                            "fields": [
                                {
                                    "key": "application-name",
                                    "title": "Applicant name",
                                    "type": "text",
                                    "answer": "Jack-Simon",
                                },
                                {
                                    "key": "upload-file",
                                    "title": "Upload file",
                                    "type": "file",
                                    "answer": "012ba4c7-e4971/test-one_two.three/programmer.jpeg",  # noqa
                                },
                                {
                                    "key": "boolean-question-1",
                                    "title": "Boolean Question 1 ",
                                    "type": "list",
                                    "answer": False,
                                },
                                {
                                    "key": "boolean-question-2",
                                    "title": "Boolean Question 2",
                                    "type": "list",
                                    "answer": True,
                                },
                            ],
                        }
                    ],
                }
            ],
        },
    },
}
