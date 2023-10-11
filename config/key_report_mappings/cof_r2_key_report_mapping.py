from config.key_report_mappings.model import extract_postcode
from config.key_report_mappings.model import KeyReportMapping
from config.key_report_mappings.model import MappingItem

COF_R2_KEY_REPORT_MAPPING = KeyReportMapping(
    round_id="c603d114-5364-4474-a0c4-c41cbf4d3bbd",
    mapping=[
        MappingItem(
            form_name="organisation-information",
            form_name_cy="gwybodaeth-am-y-sefydliad",
            key="WWWWxy",
            return_field="eoi_reference",
        ),
        MappingItem(
            form_name="organisation-information",
            form_name_cy="gwybodaeth-am-y-sefydliad",
            key="YdtlQZ",
            return_field="organisation_name",
        ),
        MappingItem(
            form_name="organisation-information",
            form_name_cy="gwybodaeth-am-y-sefydliad",
            key="lajFtB",
            return_field="organisation_type",
        ),
        MappingItem(
            form_name="asset-information",
            form_name_cy="gwybodaeth-am-yr-ased",
            key="yaQoxU",
            return_field="asset_type",
        ),
        MappingItem(
            form_name="project-information",
            form_name_cy="gwybodaeth-am-y-prosiect",
            key="yEmHpp",
            return_field="geography",
            formatter=extract_postcode,
        ),
        MappingItem(
            form_name="funding-required",
            form_name_cy="cyllid-sydd-ei-angen",
            key="JzWvhj",
            return_field="capital",
        ),
        MappingItem(
            form_name="funding-required",
            form_name_cy="cyllid-sydd-ei-angen",
            key="jLIgoi",
            return_field="revenue",
        ),
        MappingItem(
            form_name="organisation-information-ns",
            key="opFJRm",
            return_field="organisation_name_nstf",
        ),
    ],
)
