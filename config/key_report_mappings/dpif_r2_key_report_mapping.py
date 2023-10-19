from config.key_report_mappings.model import FormMappingItem
from config.key_report_mappings.model import KeyReportMapping

DPIF_R2_KEY_REPORT_MAPPING = KeyReportMapping(
    round_id="0059aad4-5eb5-11ee-8c99-0242ac120002",
    mapping=[
        FormMappingItem(
            form_name="organisation-information-dpi",
            key="IRugBv",
            return_field="applicant_email",
        ),
        FormMappingItem(
            form_name="organisation-information-dpi",
            key="nYJiWy",
            return_field="organisation_name",
        ),
    ],
)
