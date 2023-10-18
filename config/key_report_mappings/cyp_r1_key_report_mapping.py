from config.key_report_mappings.model import FormMappingItem
from config.key_report_mappings.model import KeyReportMapping

CYP_R1_KEY_REPORT_MAPPING = KeyReportMapping(
    round_id="888aae3d-7e2c-4523-b9c1-95952b3d1644",
    mapping=[
        FormMappingItem(
            form_name="applicant-information-cyp",
            key="BKOHaM",
            return_field="applicant_email",
        ),
        FormMappingItem(
            form_name="about-your-organisation-cyp",
            key="JbmcJE",
            return_field="organisation_name",
        ),
    ],
)
