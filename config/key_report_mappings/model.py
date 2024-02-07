import re
from dataclasses import dataclass
from typing import Any
from typing import Callable


@dataclass
class MappingItem:
    return_field: str
    formatter: Callable[[Any], Any] = None


@dataclass
class FormMappingItem(MappingItem):
    key: str | None = None
    form_name: str | None = None
    form_name_cy: str | None = None

    def get_form_name(self, language: str = "en"):
        if language == "cy":
            return self.form_name_cy
        return self.form_name

    def format_answer(self, field: dict) -> str:
        if (answer := field.get("answer")) and self.formatter:
            return self.formatter(answer)
        return answer  # no formatting required by default


@dataclass
class ApplicationColumnMappingItem(MappingItem):
    column_name: str | None = None

    def format_answer(self, data: Any) -> str:
        if data and self.formatter:
            return self.formatter(data)
        return data


@dataclass
class KeyReportMapping:
    round_id: str
    mapping: list[MappingItem]


# this was extracted from existing functionality, not a fan of regex for this
def extract_postcode(postcode: str) -> str | None:
    postcode = re.search(
        "([A-Za-z][A-Ha-hJ-Yj-y]?[0-9][A-Za-z0-9]? ?[0-9][A-Za-z]{2}|[Gg][Ii][Rr] ?0[Aa]{2})",  # noqa
        postcode,
    )
    if postcode:
        return postcode.group()
