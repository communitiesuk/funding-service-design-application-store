import pytest
from db.models import Applications
from db.models import Forms
from db.queries.application import process_files
from db.queries.reporting.queries import export_application_statuses_to_csv
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
