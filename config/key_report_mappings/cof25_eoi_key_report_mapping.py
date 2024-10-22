from config.key_report_mappings.model import extract_postcode
from config.key_report_mappings.model import FormMappingItem
from config.key_report_mappings.model import KeyReportMapping

COF25_EOI_KEY_REPORT_MAPPING = KeyReportMapping(
    round_id="9104d809-0fb0-4144-b514-55e81cc2b6fa",
    mapping=[
        FormMappingItem(
            form_name="organisation-details-25",
            form_name_cy="manylion-y-sefydliad",
            key="SMRWjl",
            return_field="organisation_name",
        ),
        FormMappingItem(
            form_name="development-support-provider-25",
            form_name_cy="darparwr-cymorth-datblygu",
            key="xWnVof",
            return_field="lead_contact_name",
        ),
        FormMappingItem(
            form_name="about-your-asset-25",
            form_name_cy="ynglyn-ach-ased",
            key="Ihjjyi",
            return_field="asset_type",
        ),
        FormMappingItem(
            form_name="about-your-asset-25",
            form_name_cy="ynglyn-ach-ased",
            key="dnqIdW",
            return_field="geography",
            formatter=extract_postcode,
        ),
        FormMappingItem(
            form_name="your-funding-request-25",
            form_name_cy="eich-cais-am-gyllid",
            key="fZAMFv",
            return_field="capital",
        ),
        FormMappingItem(
            form_name="development-support-provider-25",
            form_name_cy="darparwr-cymorth-datblygu",
            key="NQoGIm",
            return_field="applicant_email",
        ),
    ],
)
