from dateutil import parser as date_parser

initial_fund_store_state = {
    "slugified_test_fund_name": [
        {
            "id": "uuidv4",
            "name": "Test Fund Name",
            "questions": [
                {
                    "question": "Q1",
                    "status": "NOT STARTED",
                    "fields": [
                        {
                            "key": "applicant_name",
                            "title": "Applicant name",
                            "type": "text",
                            "answer": "Applicant",
                        }
                    ],
                },
                {
                    "question": "Q2",
                    "status": "COMPLETED",
                    "fields": [
                        {
                            "key": "applicant_name",
                            "title": "Applicant name",
                            "type": "text",
                            "answer": "Applicant",
                        }
                    ],
                },
            ],
            "date_submitted": date_parser.parse("2021-12-24 00:00:00"),
        },
        {
            "id": "uuidv4-2",
            "name": "Test Fund Name",
            "questions": [
                {
                    "question": "Q1",
                    "status": "NOT STARTED",
                    "fields": [
                        {
                            "key": "applicant_name",
                            "title": "Applicant name",
                            "type": "text",
                            "answer": "Applicant",
                        }
                    ],
                }
            ],
            "date_submitted": date_parser.parse("2022-12-25 00:00:00"),
        },
    ]
}

initial_fund_store_application = {
    "name": "Funding Service Design",
    "questions": [
        {
            "question": "About you",
            "fields": [
                {
                    "key": "applicant_name",
                    "title": "Applicant name",
                    "type": "text",
                    "answer": "Saint Nicholas",
                },
                {
                    "key": "email-about-you",
                    "title": "Email",
                    "type": "text",
                    "answer": "santa@sleighing_it.com",
                },
                {
                    "key": "applicant_telephone_number",
                    "title": "Telephone number",
                    "type": "text",
                    "answer": "121212121212",
                },
                {
                    "key": "NXTkod",
                    "title": "Website",
                    "type": "text",
                    "answer": "http://www.north-pole-here.com",
                },
            ],
            "index": 0,
        },
        {
            "category": "kfFsQz",
            "question": "About your organisation",
            "fields": [
                {
                    "key": "org_name",
                    "title": "Organisation name",
                    "type": "text",
                    "answer": "Presents-R-US inc.",
                },
                {
                    "key": "org_address",
                    "title": "Organisation address",
                    "type": "text",
                    "answer": "1 North Pole",
                },
                {
                    "key": "org_type",
                    "title": "Type of organisation",
                    "type": "list",
                    "answer": "PLC",
                },
                {
                    "key": "delivered_before",
                    "title": "Have you delivered projects like this before?",
                    "type": "list",
                    "answer": "true",
                },
                {
                    "key": "evidence_of_prev_projects",
                    "title": "Upload evidence to support your answer",
                    "type": "file",
                    "answer": "null",
                },
            ],
            "index": 0,
        },
        {
            "category": "cxVIPK",
            "question": "About your organisation",
            "fields": [
                {
                    "key": "org_accountant",
                    "title": "Your Accountant",
                    "type": "text",
                    "answer": "Mrs Claus",
                },
                {
                    "key": "uoDsSL",
                    "title": "Responsible person",
                    "type": "text",
                    "answer": "The Snowman",
                },
                {
                    "key": "cFmoxP",
                    "title": (
                        "Do you have endorsements to support your application?"
                    ),
                    "type": "list",
                    "answer": "false",
                },
                {
                    "key": "QKxzxf",
                    "title": "Who is endorsing your application?",
                    "type": "text",
                    "answer": "The tooth fairy",
                },
                {
                    "key": "ymIxKr",
                    "title": "Upload evidence to support your answer",
                    "type": "file",
                    "answer": "null",
                },
            ],
            "index": 0,
        },
        {
            "question": "Choose your country",
            "fields": [
                {
                    "key": "country",
                    "title": "What country is your project in",
                    "type": "list",
                    "answer": "england",
                }
            ],
            "index": 0,
        },
        {
            "question": "England",
            "fields": [
                {
                    "key": "local_authority",
                    "title": "What local authority is your project in?",
                    "type": "list",
                    "answer": "Adur and Worthing Borough Council",
                }
            ],
            "index": 0,
        },
        {
            "category": "null",
            "question": "Declaration",
            "fields": [
                {
                    "key": "declaration",
                    "title": "Declaration",
                    "type": "boolean",
                    "answer": "true",
                }
            ],
        },
    ],
    "metadata": {"paymentSkipped": "false"},
}
