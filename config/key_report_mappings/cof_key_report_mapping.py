from config.key_report_mappings.model import ApplicationColumnMappingItem
from config.key_report_mappings.model import extract_postcode
from config.key_report_mappings.model import FormMappingItem
from config.key_report_mappings.model import KeyReportMapping

COF_KEY_REPORT_MAPPING = KeyReportMapping(
    round_id=["4efc3263-aefe-4071-b5f4-0910abec12d2", "33726b63-efce-4749-b149-20351346c76e"],
    mapping=[
        FormMappingItem(
            form_name="applicant-information-cof",
            form_name_cy="gwybodaeth-am-yr-ymgeisydd-cof",
            key="NlHSBg",
            return_field="applicant_email",
        ),
        FormMappingItem(
            form_name="organisation-information-cof",
            form_name_cy="gwybodaeth-am-y-sefydliad-cof",
            key="WWWWxy",
            return_field="eoi_reference",
        ),
        FormMappingItem(
            form_name="organisation-information-cof",
            form_name_cy="gwybodaeth-am-y-sefydliad-cof",
            key="YdtlQZ",
            return_field="organisation_name",
        ),
        FormMappingItem(
            form_name="organisation-information-cof",
            form_name_cy="gwybodaeth-am-y-sefydliad-cof",
            key="lajFtB",
            return_field="organisation_type",
        ),
        FormMappingItem(
            form_name="asset-information-cof",
            form_name_cy="gwybodaeth-am-yr-ased-cof",
            key="oXGwlA",
            return_field="asset_type",
        ),
        FormMappingItem(
            form_name="asset-information-cof",
            form_name_cy="gwybodaeth-am-yr-ased-cof",
            key="aJGyCR",
            return_field="asset_type_other",
        ),
        FormMappingItem(
            form_name="project-information-cof",
            form_name_cy="gwybodaeth-am-y-prosiect-cof",
            key="EfdliG",
            return_field="geography",
            formatter=extract_postcode,
        ),
        FormMappingItem(
            form_name="funding-required-cof",
            form_name_cy="cyllid-sydd-ei-angen-cof",
            key="ABROnB",
            return_field="capital",
        ),
        FormMappingItem(
            form_name="funding-required-cof",
            form_name_cy="cyllid-sydd-ei-angen-cof",
            key="tSKhQQ",
            return_field="revenue",
            formatter=lambda answer: sum([x["UyaAHw"] for x in answer or []]),
        ),
        ApplicationColumnMappingItem(
            column_name="reference",
            return_field="ref",
        ),
        ApplicationColumnMappingItem(
            column_name="id",
            return_field="link",
        ),  # noqa
        FormMappingItem(
            form_name="project-information-cof",
            form_name_cy="gwybodaeth-am-y-prosiect-cof",
            key="apGjFS",
            return_field="project_name",
        ),
    ],
)
