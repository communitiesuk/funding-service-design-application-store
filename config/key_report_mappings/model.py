import re
from dataclasses import dataclass


@dataclass
class MappingItem:
    key: str
    return_field: str
    form_name: str
    form_name_cy: str | None = None

    def get_form_name(self, language: str = "en"):
        if language == "cy":
            return self.form_name_cy
        return self.form_name

    def format_answer(self, field: dict) -> str:
        return field.get("answer")  # no formatting required by default


@dataclass
class PostcodeMappingItem(MappingItem):
    def format_answer(self, field: dict) -> str:
        if answer := field.get("answer"):
            return extract_postcode(answer)
        return super().format_answer(field)


@dataclass
class MultiInputChildSum(MappingItem):
    child_key: str | None = None

    def format_answer(self, field: dict) -> int:
        list_of_child_dicts: list[dict] = field.get("answer")
        return sum([x[self.child_key] for x in list_of_child_dicts])


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
