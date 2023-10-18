from config.key_report_mappings.model import ApplicationColumnMappingItem
from config.key_report_mappings.model import extract_postcode
from config.key_report_mappings.model import FormMappingItem
from config.key_report_mappings.model import KeyReportMapping

COF_R3W2_KEY_REPORT_MAPPING = KeyReportMapping(
    round_id="6af19a5e-9cae-4f00-9194-cf10d2d7c8a7",
    mapping=[
        FormMappingItem(
            form_name="applicant-information-cof-r3-w2",
            form_name_cy="gwybodaeth-am-yr-ymgeisydd-cof-r3-w2",
            key="NlHSBg",
            return_field="applicant_email",
        ),
        FormMappingItem(
            form_name="organisation-information-cof-r3-w2",
            form_name_cy="gwybodaeth-am-y-sefydliad-cof-r3-w2",
            key="WWWWxy",
            return_field="eoi_reference",
        ),
        FormMappingItem(
            form_name="organisation-information-cof-r3-w2",
            form_name_cy="gwybodaeth-am-y-sefydliad-cof-r3-w2",
            key="YdtlQZ",
            return_field="organisation_name",
        ),
        FormMappingItem(
            form_name="organisation-information-cof-r3-w2",
            form_name_cy="gwybodaeth-am-y-sefydliad-cof-r3-w2",
            key="lajFtB",
            return_field="organisation_type",
        ),
        FormMappingItem(
            form_name="asset-information-cof-r3-w2",
            form_name_cy="gwybodaeth-am-yr-ased-cof-r3-w2",
            key="oXGwlA",
            return_field="asset_type",
        ),
        FormMappingItem(
            form_name="asset-information-cof-r3-w2",
            form_name_cy="gwybodaeth-am-yr-ased-cof-r3-w2",
            key="aJGyCR",
            return_field="asset_type_other",
        ),
        FormMappingItem(
            form_name="project-information-cof-r3-w2",
            form_name_cy="gwybodaeth-am-y-prosiect-cof-r3-w2",
            key="EfdliG",
            return_field="geography",
            formatter=extract_postcode,
        ),
        FormMappingItem(
            form_name="funding-required-cof-r3-w2",
            form_name_cy="cyllid-sydd-ei-angen-cof-r3-w2",
            key="ABROnB",
            return_field="capital",
        ),
        FormMappingItem(
            form_name="funding-required-cof-r3-w2",
            form_name_cy="cyllid-sydd-ei-angen-cof-r3-w2",
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
        ),
        # ApplicationColumnMappingItem(    # think we'd need to add a concept for grabbing email by account id    # noqa
        #     column_name="email",         # however that data belongs in the account-store                       # noqa
        #     return_field="account_id"                                                                           # noqa
        # ),                                                                                                      # noqa
        FormMappingItem(
            form_name="project-information-cof-r3-w2",
            form_name_cy="gwybodaeth-am-y-prosiect-cof-r3-w2",
            key="apGjFS",
            return_field="project_name",
        ),
    ],
)
