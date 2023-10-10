import pytest
from config.key_report_mappings.cof_r2_key_report_mapping import (
    COF_R2_KEY_REPORT_MAPPING,
)
from config.key_report_mappings.cof_r3w2_key_report_mapping import (
    COF_R3W2_KEY_REPORT_MAPPING,
)
from config.key_report_mappings.model import extract_postcode
from db.models import Applications
from db.models import Forms
from db.queries.application import process_files
from db.queries.reporting.queries import export_application_statuses_to_csv
from db.queries.reporting.queries import map_application_key_fields
from external_services.aws import FileData


@pytest.mark.parametrize(
    "application, all_application_files, expected",
    [
        pytest.param(
            Applications(
                forms=[
                    Forms(
                        json=[
                            {
                                "fields": [
                                    {"key": "not_a_file_component", "answer": None}
                                ]
                            }
                        ]
                    )
                ]
            ),
            [FileData("app1", "form1", "path1", "component1", "file1.docx")],
            Applications(
                forms=[
                    Forms(
                        json=[
                            {
                                "fields": [
                                    {"key": "not_a_file_component", "answer": None}
                                ]
                            }
                        ]
                    )
                ]
            ),
            id="Irrelevant components are ignored",
        ),
        pytest.param(
            Applications(
                forms=[
                    Forms(json=[{"fields": [{"key": "component1", "answer": None}]}]),
                    Forms(json=[{"fields": [{"key": "component2", "answer": None}]}]),
                ]
            ),
            [
                FileData("app1", "form1", "path1", "component1", "file1.docx"),
                FileData("app1", "form1", "path1", "component2", "file2.docx"),
            ],
            Applications(
                forms=[
                    Forms(
                        json=[
                            {"fields": [{"key": "component1", "answer": "file1.docx"}]}
                        ]
                    ),
                    Forms(
                        json=[
                            {"fields": [{"key": "component2", "answer": "file2.docx"}]}
                        ]
                    ),
                ]
            ),
            id="Multiple forms all work as expected",
        ),
        pytest.param(
            Applications(
                forms=[
                    Forms(json=[{"fields": [{"key": "component1", "answer": None}]}])
                ]
            ),
            [FileData("app1", "form1", "path1", "component1", "file1.docx")],
            Applications(
                forms=[
                    Forms(
                        json=[
                            {"fields": [{"key": "component1", "answer": "file1.docx"}]}
                        ]
                    )
                ]
            ),
            id="Single file available for a component",
        ),
        pytest.param(
            Applications(
                forms=[
                    Forms(json=[{"fields": [{"key": "component1", "answer": None}]}])
                ]
            ),
            [
                FileData("app1", "form1", "path1", "component1", "file1.docx"),
                FileData("app1", "form1", "path2", "component1", "file2.pdf"),
                FileData("app1", "form1", "path3", "component1", "file3.txt"),
            ],
            Applications(
                forms=[
                    Forms(
                        json=[
                            {
                                "fields": [
                                    {
                                        "key": "component1",
                                        "answer": "file1.docx, file2.pdf, file3.txt",
                                    }
                                ]
                            }
                        ]
                    )
                ]
            ),
            id="Multiple files available for a component",
        ),
        pytest.param(
            Applications(
                forms=[
                    Forms(
                        json=[
                            {
                                "fields": [
                                    {"key": "component1", "answer": None},
                                    {"key": "component2", "answer": None},
                                ]
                            }
                        ]
                    )
                ]
            ),
            [
                FileData("app1", "form1", "path1", "component1", "file1.docx"),
                FileData("app1", "form1", "path2", "component1", "file2.pdf"),
                FileData("app1", "form1", "path3", "component2", "file3.txt"),
            ],
            Applications(
                forms=[
                    Forms(
                        json=[
                            {
                                "fields": [
                                    {
                                        "key": "component1",
                                        "answer": "file1.docx, file2.pdf",
                                    },
                                    {"key": "component2", "answer": "file3.txt"},
                                ]
                            }
                        ]
                    )
                ]
            ),
            id="Files available for multiple components",
        ),
    ],
)
def test_process_files(application, all_application_files, expected):
    """
    GIVEN an application object and a list of all files belonging to that application
    WHEN the process_files function is invoked with these parameters
    THEN the application object is expected to be updated with the relevant file information
    """
    result = process_files(application, all_application_files)
    for form, expected_form in zip(result.forms, expected.forms):
        assert form.json == pytest.approx(expected_form.json)


@pytest.mark.parametrize(
    "data,lines_exp",
    [
        (
            [
                {
                    "fund_id": "111",
                    "rounds": [
                        {
                            "round_id": "r1r1r1",
                            "application_statuses": {
                                "NOT_STARTED": 1,
                                "IN_PROGRESS": 2,
                                "COMPLETED": 3,
                                "SUBMITTED": 4,
                            },
                        }
                    ],
                }
            ],
            ["111,r1r1r1,1,2,3,4"],
        ),
        (
            [
                {
                    "fund_id": "111",
                    "rounds": [
                        {
                            "round_id": "r1r1r1",
                            "application_statuses": {
                                "NOT_STARTED": 1,
                                "IN_PROGRESS": 2,
                                "COMPLETED": 3,
                                "SUBMITTED": 4,
                            },
                        },
                        {
                            "round_id": "r2",
                            "application_statuses": {
                                "NOT_STARTED": 2,
                                "IN_PROGRESS": 3,
                                "COMPLETED": 4,
                                "SUBMITTED": 5,
                            },
                        },
                    ],
                }
            ],
            ["111,r1r1r1,1,2,3,4", "111,r2,2,3,4,5"],
        ),
        (
            [
                {
                    "fund_id": "f1",
                    "rounds": [
                        {
                            "round_id": "r1",
                            "application_statuses": {
                                "NOT_STARTED": 1,
                                "IN_PROGRESS": 2,
                                "COMPLETED": 3,
                                "SUBMITTED": 4,
                            },
                        },
                        {
                            "round_id": "r2",
                            "application_statuses": {
                                "NOT_STARTED": 0,
                                "IN_PROGRESS": 0,
                                "COMPLETED": 0,
                                "SUBMITTED": 4,
                            },
                        },
                    ],
                },
                {
                    "fund_id": "f2",
                    "rounds": [
                        {
                            "round_id": "r1",
                            "application_statuses": {
                                "NOT_STARTED": 2,
                                "IN_PROGRESS": 2,
                                "COMPLETED": 1,
                                "SUBMITTED": 6,
                            },
                        },
                    ],
                },
            ],
            ["f1,r1,1,2,3,4", "f1,r2,0,0,0,4", "f2,r1,2,2,1,6"],
        ),
    ],
)
def test_application_status_csv(data, lines_exp):
    result = export_application_statuses_to_csv(data)
    assert result
    lines = result.readlines()
    assert (
        lines[0].decode().strip()
        == "fund_id,round_id,NOT_STARTED,IN_PROGRESS,COMPLETED,SUBMITTED"
    )
    idx = 1
    for line in lines_exp:
        assert lines[idx].decode().strip() == line
        idx += 1


@pytest.mark.parametrize(
    "input_str, expected_output",
    [
        # Valid postcodes
        ("SW1A 1AA", "SW1A 1AA"),
        ("BD23 1DN", "BD23 1DN"),
        ("W1A 0AX", "W1A 0AX"),
        ("GIR 0AA", "GIR 0AA"),  # special case for GIR 0AA
        # Invalid postcodes
        ("123456", None),
        ("ABCDEFG", None),
        ("XYZ 123", None),
        # Mixed strings
        ("My postcode is SW1A 1AA in London.", "SW1A 1AA"),
        ("The code is BD23 1DN for that location.", "BD23 1DN"),
        ("No postcode here.", None),
    ],
)
def test_extract_postcode(input_str, expected_output):
    assert extract_postcode(input_str) == expected_output


@pytest.mark.parametrize(
    "mapping, application, expected_output",
    [
        (
            COF_R2_KEY_REPORT_MAPPING.mapping,
            {
                "language": "en",
                "forms": [
                    {
                        "name": "organisation-information",
                        "questions": [
                            {
                                "fields": [
                                    {"key": "WWWWxy", "answer": "Ref1234"},
                                    {"key": "YdtlQZ", "answer": "OrgName"},
                                    {"key": "lajFtB", "answer": "Non-Profit"},
                                ]
                            }
                        ],
                    },
                    {
                        "name": "asset-information",
                        "questions": [
                            {
                                "fields": [
                                    {"key": "yaQoxU", "answer": "Building"},
                                ]
                            }
                        ],
                    },
                    {
                        "name": "project-information",
                        "questions": [
                            {
                                "fields": [
                                    {"key": "yEmHpp", "answer": "GIR 0AA"},
                                ]
                            }
                        ],
                    },
                    {
                        "name": "funding-required",
                        "questions": [
                            {
                                "fields": [
                                    {"key": "JzWvhj", "answer": "50000"},
                                    {"key": "jLIgoi", "answer": "10000"},
                                ]
                            }
                        ],
                    },
                    {
                        "name": "organisation-information-ns",
                        "questions": [
                            {
                                "fields": [
                                    {"key": "opFJRm", "answer": "OrgName NSTF"},
                                ]
                            }
                        ],
                    },
                ],
            },
            {
                "eoi_reference": "Ref1234",
                "organisation_name": "OrgName",
                "organisation_type": "Non-Profit",
                "asset_type": "Building",
                "geography": "GIR 0AA",
                "capital": "50000",
                "revenue": "10000",
                "organisation_name_nstf": "OrgName NSTF",
            },
        ),
        (
            COF_R3W2_KEY_REPORT_MAPPING.mapping,
            {
                "language": "en",
                "forms": [],
            },
            {
                "eoi_reference": "Ref1234",
                "organisation_name": "OrgName",
                "organisation_type": "Non-Profit",
                "asset_type": "Building",
                "geography": "GIR 0AA",
                "capital": "50000",
                "revenue": "10000",
                "organisation_name_nstf": "OrgName NSTF",
            },
        ),
    ],
)
def test_map_application_key_fields(mapping, application, expected_output):
    result = map_application_key_fields(application, mapping)
    assert result == expected_output
