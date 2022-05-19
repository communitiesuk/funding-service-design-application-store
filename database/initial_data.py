from dateutil import parser as date_parser

initial_application_store_state = {
    "uuidv4": {
        "id": "uuidv4",
        "status": "COMPLETED",
        "fund_id": "test-fund-name",
        "fund_name": "Test Fund Name",
        "round_id": "spring",
        "date_submitted": date_parser.parse("2021-12-24 00:00:00"),
        "assessment_deadline": date_parser.parse("2022-08-28 00:00:00"),
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
                "category": "",
                "index": 0,
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
                "category": "",
                "index": 0,
            },
        ],
        "metadata": {"paymentSkipped": "false"},
    },
    "uuidv4-2": {
        "id": "uuidv4-2",
        "status": "NOT_STARTED",
        "fund_id": "test-fund-name",
        "fund_name": "Test Fund Name",
        "round_id": "spring",
        "date_submitted": date_parser.parse("2022-12-25 00:00:00"),
        "assessment_deadline": date_parser.parse("2022-08-28 00:00:00"),
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
                "category": "",
                "index": 0,
            }
        ],
        "metadata": {"paymentSkipped": "false"},
    },
}

initial_macro_application = {
    "account_id": "AccountA",
    "fund_id": "Community ownership fund application",
    "round_id": "Round Two",
    "sections": [
        {
            "status": "Incomplete",
            "payload": {
                "name": "about-your-org",
                "questions": [
                    {
                        "question": "Application information",
                        "fields": [
                            {
                                "key": "application-name",
                                "title": "Applicant name",
                                "type": "text",
                                "answer": ""
                            },
                            {
                                "key": "applicant-email",
                                "title": "Email",
                                "type": "text",
                                "answer": ""
                            },
                            {
                                "key": "applicant-telephone-number",
                                "title": "Telephone number",
                                "type": "text",
                                "answer": ""
                            },
                            {
                                "key": "applicant-website",
                                "title": "Website",
                                "type": "text",
                                "answer": ""
                            }
                        ]
                    },
                    {
                        "question": "Organisation information",
                        "fields": [
                            {
                                "key": "organisation-name",
                                "title": "Organisation name",
                                "type": "text",
                                "answer": ""
                            },
                            {
                                "key": "organisation-address",
                                "title": "Organisation address",
                                "type": "text",
                                "answer": ""
                            },
                            {
                                "key": "type-of-organisation",
                                "title": "Type of organisation",
                                "type": "list",
                                "answer": ""
                            },
                            {
                                "key": "delivered-projects-like-this-before",
                                "title": "Have you delivered projects like this before?",
                                "type": "list",
                                "answer": ""
                            }
                        ]
                    },
                    {
                        "question": "Responsible people",
                        "fields": [
                            {
                                "key": "organisation-accountant",
                                "title": "Your accountant",
                                "type": "text",
                                "answer": ""
                            },
                            {
                                "key": "responsible-person",
                                "title": "Responsible person",
                                "type": "text",
                                "answer": ""
                            },
                            {
                                "key": "SpLmlI",
                                "title": "Do you have endorsements for this ",
                                "type": "list",
                                "answer": ""
                            },
                            {
                                "key": "organisation-do-you-have-endorsements",
                                "title": "Do you have endorsements to support your application?",
                                "type": "list",
                                "answer": ""
                            },
                            {
                                "key": "who-is-endorsing-your-application",
                                "title": "Who is endorsing your application?",
                                "type": "list",
                                "answer": ""
                            }
                        ]
                    }
                ],
                "metadata": {
                    "application_id": "1"
                }
            },
            "section_name": "about-your-org"
        },
        {
            "status": "Incomplete",
            "payload": {
                "name": "about-your-project",
                "questions": [
                    {
                        "question": "Project details",
                        "fields": [
                            {
                                "key": "your-project-name",
                                "title": "Project name",
                                "type": "text",
                                "answer": "Test Project"
                            },
                            {
                                "key": "your-project-location",
                                "title": "Project location",
                                "type": "text",
                                "answer": "Test Address, Testville, T12 2re"
                            },
                            {
                                "key": "your-project-sector",
                                "title": "Project sector",
                                "type": "list",
                                "answer": "1"
                            },
                            {
                                "key": "your-project-long-description",
                                "title": "Project description",
                                "type": "text",
                                "answer": "Test"
                            },
                            {
                                "key": "your-project-short-description",
                                "title": "Project summary",
                                "type": "text",
                                "answer": "Test"
                            }
                        ]
                    },
                    {
                        "question": "Funding requested",
                        "fields": [
                            {
                                "key": "about-your-project-capital-expenditure",
                                "title": "Capital expenditure",
                                "type": "text",
                                "answer": "1"
                            },
                            {
                                "key": "about-your-project-revenue",
                                "title": "Revenue",
                                "type": "text",
                                "answer": "1"
                            },
                            {
                                "key": "about-your-project-subsidy",
                                "title": "Subsidy",
                                "type": "text",
                                "answer": "1"
                            }
                        ]
                    },
                    {
                        "question": "Project aims",
                        "fields": [
                            {
                                "key": "about-your-project-policy-aims",
                                "title": "Which policy aims will your project deliver against?",
                                "type": "list",
                                "answer": [
                                    "Net zero"
                                ]
                            }
                        ]
                    }
                ],
                "metadata": {
                    "paymentSkipped": "false",
                    "application_id": "1"
                }
            },
            "section_name": "about-your-project"
        },
        {
            "status": "Incomplete",
            "payload": {
                "name": "plan-your-project",
                "questions": [
                    {
                        "question": "Plan your project",
                        "fields": [
                            {
                                "key": "plan-your-project-start-date",
                                "title": "When will you start your project?",
                                "type": "monthYear",
                                "answer": "2025-01"
                            },
                            {
                                "key": "plan-your-project-activity-name",
                                "title": "Activity",
                                "type": "text",
                                "answer": "Test"
                            },
                            {
                                "key": "plan-your-project-activity-duration",
                                "title": "Duration",
                                "type": "text",
                                "answer": "Test"
                            },
                            {
                                "key": "plan-your-project-activity-cost",
                                "title": "Cost",
                                "type": "text",
                                "answer": "1"
                            }
                        ]
                    },
                    {
                        "question": "Delivery partner",
                        "fields": [
                            {
                                "key": "plan-your-project-will-work-with-delivery-partner",
                                "title": "Will you work with a delivery partner on this project?",
                                "type": "list",
                                "answer": "true"
                            }
                        ]
                    },
                    {
                        "question": "Plan your project (With Delivery Partner Page)",
                        "fields": [
                            {
                                "key": "plan-your-project-delivery-partner",
                                "title": "Who is your delivery partner on this project?",
                                "type": "text",
                                "answer": "Test"
                            },
                            {
                                "key": "plan-your-project-why-this-partner",
                                "title": "Why is this delivery partner the best choice for this project?",
                                "type": "text",
                                "answer": "Test"
                            },
                            {
                                "key": "plan-your-project-what-skills",
                                "title": "What skills and expertise are needed to deliver this project?",
                                "type": "text",
                                "answer": "Test"
                            }
                        ]
                    },
                    {
                        "question": "Plan your project (without delivery partner page)",
                        "fields": [
                            {
                                "key": "plan-your-project-internal-resources",
                                "title": "Do you have the internal resources needed to deliver this project?",
                                "type": "list",
                                "answer": "true"
                            },
                            {
                                "key": "plan-your-project-how-did-you-internal-resources",
                                "title": "If yes to the above, how did you work that out?",
                                "type": "text",
                                "answer": "Test"
                            },
                            {
                                "key": "plan-your-project-how-will-you-recruit-resources",
                                "title": "If no, tell us how you are going to recruit the resources you need",
                                "type": "text",
                                "answer": "Test"
                            },
                            {
                                "key": "plan-your-project-which-skills-needed",
                                "title": "What skills and expertise are needed to deliver this project?",
                                "type": "text",
                                "answer": "Test"
                            }
                        ]
                    },
                    {
                        "question": "Who will govern",
                        "fields": [
                            {
                                "key": "plan-your-project-govern-role",
                                "title": "Role",
                                "type": "text",
                                "answer": "Test"
                            },
                            {
                                "key": "plan-your-project-govern-resposibility",
                                "title": "Responsibility",
                                "type": "text",
                                "answer": "Test"
                            }
                        ]
                    },
                    {
                        "question": "Governance processes",
                        "fields": [
                            {
                                "key": "plan-your-project-what-governance-processes",
                                "title": "What governance processes do you have in place to make sure the project succeeds?",
                                "type": "text",
                                "answer": "Test"
                            }
                        ]
                    }
                ],
                "metadata": {
                    "paymentSkipped": "false",
                    "application_id": "1"
                }
            },
            "section_name": "plan-your-project"
        },
        {
            "status": "Incomplete",
            "payload": {
                "name": "deliver-your-project",
                "questions": [
                    {
                        "category": "ZtqkbP",
                        "question": "What your project benefits are",
                        "fields": [
                            {
                                "key": "eblbkX",
                                "title": "Outcome 1",
                                "type": "text",
                                "answer": "Test"
                            },
                            {
                                "key": "oQEWUg",
                                "title": "Outcome 2",
                                "type": "text",
                                "answer": "Test"
                            }
                        ]
                    },
                    {
                        "category": "ZtqkbP",
                        "question": "Who your project benefits",
                        "fields": [
                            {
                                "key": "YaGZms",
                                "title": "Who does your project benefit?",
                                "type": "text",
                                "answer": "Test"
                            },
                            {
                                "key": "SYlMhT",
                                "title": "How can you prove this quantitatively?",
                                "type": "text",
                                "answer": "Test"
                            },
                            {
                                "key": "MNkdUT",
                                "title": "How can you prove this qualitatively?",
                                "type": "text",
                                "answer": "Test"
                            }
                        ]
                    },
                    {
                        "category": "ZtqkbP",
                        "question": "Your project budget",
                        "fields": [
                            {
                                "key": "kKyBnL",
                                "title": "Add your costs",
                                "type": "text",
                                "answer": "Test"
                            },
                            {
                                "key": "zyfPIu",
                                "title": "Project cost type",
                                "type": "list",
                                "answer": "Indirect"
                            },
                            {
                                "key": "tfqDZZ",
                                "title": "Cost",
                                "type": "text",
                                "answer": "1"
                            }
                        ]
                    },
                    {
                        "question": "Your project risks",
                        "fields": [
                            {
                                "key": "ZJUaPq",
                                "title": "Describe your organisation's attitude to risk",
                                "type": "list",
                                "answer": "Risk averse"
                            },
                            {
                                "key": "cMdGPb",
                                "title": "Explain your answer",
                                "type": "text",
                                "answer": "Test"
                            },
                            {
                                "key": "LpKdsv",
                                "title": "How does your organisation balance innovation with risk?",
                                "type": "text",
                                "answer": "Test"
                            }
                        ]
                    },
                    {
                        "category": "ZtqkbP",
                        "question": "Your risk register",
                        "fields": [
                            {
                                "key": "WcJUsi",
                                "title": "Risk",
                                "type": "text",
                                "answer": "Test"
                            },
                            {
                                "key": "OecMxU",
                                "title": "Mitigation",
                                "type": "text",
                                "answer": "Test"
                            },
                            {
                                "key": "rDyIBy",
                                "title": "Risk Level",
                                "type": "list",
                                "answer": "high"
                            },
                            {
                                "key": "XBxwLy",
                                "title": "Categorise your risk",
                                "type": "list",
                                "answer": "reputational risk"
                            }
                        ]
                    },
                    {
                        "category": "ZtqkbP",
                        "question": "How you manage risk",
                        "fields": [
                            {
                                "key": "NNYdkz",
                                "title": "Tell us how you identified the risks in your risk register",
                                "type": "text",
                                "answer": "Test"
                            },
                            {
                                "key": "ihDAjW",
                                "title": "Tell us how you will manage the risks in your risk register",
                                "type": "text",
                                "answer": "Test"
                            }
                        ]
                    },
                    {
                        "category": "ZtqkbP",
                        "question": "Monitoring and evaluation plan",
                        "fields": [
                            {
                                "key": "mvBPSb",
                                "title": "What do you want to know?",
                                "type": "text",
                                "answer": "Test"
                            },
                            {
                                "key": "ASwuiF",
                                "title": "How will you know it?",
                                "type": "text",
                                "answer": "Test"
                            },
                            {
                                "key": "eAJwgs",
                                "title": "Where will the data come from?",
                                "type": "text",
                                "answer": "Test"
                            },
                            {
                                "key": "ktaiVA",
                                "title": "Who will capture the data?",
                                "type": "text",
                                "answer": "Test"
                            },
                            {
                                "key": "MiosEa",
                                "title": "When will data be captured?",
                                "type": "text",
                                "answer": "Test"
                            },
                            {
                                "key": "NrdwqP",
                                "title": "How much will it cost?",
                                "type": "text",
                                "answer": "Test"
                            }
                        ]
                    },
                    {
                        "category": "ZtqkbP",
                        "question": "How you measure progress",
                        "fields": [
                            {
                                "key": "VWskeQ",
                                "title": "How are you going to make sure that the project is delivered on time?",
                                "type": "text",
                                "answer": "Test"
                            },
                            {
                                "key": "iiGucM",
                                "title": "How are you going to make sure that the project is delivered on budget?",
                                "type": "text",
                                "answer": "Test"
                            }
                        ]
                    }
                ],
                "metadata": {
                    "paymentSkipped": "false",
                    "application_id": "1"
                }
            },
            "section_name": "deliver-your-project"
        },
        {
            "status": "Incomplete",
            "payload": {
                "name": "declaration",
                "questions": [
                    {
                        "question": "Declarations",
                        "fields": [
                            {
                                "key": "declarations-state-aid",
                                "title": "Would funding your organisation be classed as State Aid?",
                                "type": "list",
                                "answer": "true"
                            },
                            {
                                "key": "declarations-explain-state-aid",
                                "title": "If yes to the above, explain how your project is compliant with the UK subsidy control regime",
                                "type": "text",
                                "answer": "Test"
                            },
                            {
                                "key": "declarations-protected-characteristics",
                                "title": "Describe how your project will impact people with protected characteristics?",
                                "type": "text",
                                "answer": "Test"
                            },
                            {
                                "key": "declarations-environmental",
                                "title": "Does your application comply with all relevant environmental standards?",
                                "type": "list",
                                "answer": "false"
                            },
                            {
                                "key": "declarations-support-environmental",
                                "title": "If yes to the above, upload a file in support of your answer",
                                "type": "file",
                                "answer": "null"
                            }
                        ]
                    }
                ],
                "metadata": {
                    "paymentSkipped": "false",
                    "application_id": "1"
                }
            },
            "section_name": "declaration",
        }
    ]
}