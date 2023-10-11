import re
from dataclasses import dataclass
from typing import Any
from typing import Callable


@dataclass
class MappingItem:
    key: str
    return_field: str
    form_name: str
    form_name_cy: str | None = None
    formatter: Callable[[Any], Any] = None

    def get_form_name(self, language: str = "en"):
        if language == "cy":
            return self.form_name_cy
        return self.form_name

    def format_answer(self, field: dict) -> str:
        if (answer := field.get("answer")) and self.formatter:
            return self.formatter(answer)
        return answer  # no formatting required by default


@dataclass
class KeyReportMapping:
    round_id: str
    mapping: list[MappingItem]


# this was extracted from existing functionality, not a fan of regex for this
def extract_postcode(postcode: str) -> str | None:
    postcode = re.search(
        "([A-Za-z][A-Ha-hJ-Yj-y]?[0-9][A-Za-z0-9]?"
        " ?[0-9][A-Za-z]{2}|[Gg][Ii][Rr]"
        " ?0[Aa]{2})",  # noqa
        postcode,
    )
    if postcode:
        return postcode.group()
