from config.key_report_mappings.model import extract_postcode
from config.key_report_mappings.model import KeyReportMapping
from config.key_report_mappings.model import MappingItem

COF_R3W2_KEY_REPORT_MAPPING = KeyReportMapping(
    round_id="6af19a5e-9cae-4f00-9194-cf10d2d7c8a7",
    mapping=[
        MappingItem(
            form_name="organisation-information-cof-r3-w2",
            form_name_cy="gwybodaeth-am-y-sefydliad-cof-r3-w2",
            key="WWWWxy",
            return_field="eoi_reference",
        ),
        MappingItem(
            form_name="organisation-information-cof-r3-w2",
            form_name_cy="gwybodaeth-am-y-sefydliad-cof-r3-w2",
            key="YdtlQZ",
            return_field="organisation_name",
        ),
        MappingItem(
            form_name="organisation-information-cof-r3-w2",
            form_name_cy="gwybodaeth-am-y-sefydliad-cof-r3-w2",
            key="lajFtB",
            return_field="organisation_type",
        ),
        MappingItem(
            form_name="asset-information-cof-r3-w2",
            form_name_cy="gwybodaeth-am-yr-ased-cof-r3-w2",
            key="oXGwlA",
            return_field="asset_type",
        ),
        MappingItem(
            form_name="project-information-cof-r3-w2",
            form_name_cy="gwybodaeth-am-y-prosiect-cof-r3-w2",
            key="EfdliG",
            return_field="geography",
            formatter=extract_postcode,
        ),
        MappingItem(
            form_name="funding-required-cof-r3-w2",
            form_name_cy="cyllid-sydd-ei-angen-cof-r3-w2",
            key="ABROnB",
            return_field="capital",
        ),
        MappingItem(
            form_name="funding-required-cof-r3-w2",
            form_name_cy="cyllid-sydd-ei-angen-cof-r3-w2",
            key="tSKhQQ",
            return_field="revenue",
            formatter=lambda answer: sum([x["UyaAHw"] for x in answer or []]),
        ),
    ],
)
