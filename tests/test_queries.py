import pytest
from db.models import Applications
from db.models import Forms
from db.queries.application import process_files
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
