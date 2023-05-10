from _helpers.form import get_forms_from_sections


section_config = [
    {
        "form_name": None,
        "title": "section 1",
        "children": [
            {
                "children": [],
                "form_name": "form-a",
            },
            {
                "children": [],
                "form_name": "form-b",
            },
        ],
    },
    {
        "form_name": None,
        "title": "section 2",
        "children": [
            {
                "children": [],
                "form_name": "form-c",
            },
            {
                "children": [],
                "form_name": "form-d",
            },
        ],
    },
]


def test_get_forms_from_sections():
    form_result = get_forms_from_sections(section_config)
    assert len(form_result) == 4
    assert "form-d" in form_result
