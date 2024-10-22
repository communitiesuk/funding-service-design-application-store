from collections import defaultdict

from config.key_report_mappings.cof25_eoi_key_report_mapping import (
    COF25_EOI_KEY_REPORT_MAPPING,
)
from config.key_report_mappings.cof_eoi_key_report_mapping import (
    COF_EOI_KEY_REPORT_MAPPING,
)
from config.key_report_mappings.cof_key_report_mapping import (
    COF_KEY_REPORT_MAPPING,
)
from config.key_report_mappings.cof_r2_key_report_mapping import (
    COF_R2_KEY_REPORT_MAPPING,
)
from config.key_report_mappings.cof_r3w2_key_report_mapping import (
    COF_R3W2_KEY_REPORT_MAPPING,
)
from config.key_report_mappings.cyp_r1_key_report_mapping import (
    CYP_R1_KEY_REPORT_MAPPING,
)
from config.key_report_mappings.dpif_r2_key_report_mapping import (
    DPIF_R2_KEY_REPORT_MAPPING,
)


ROUND_ID_TO_KEY_REPORT_MAPPING = defaultdict(
    lambda: COF_R2_KEY_REPORT_MAPPING.mapping,
    {
        CYP_R1_KEY_REPORT_MAPPING.round_id: CYP_R1_KEY_REPORT_MAPPING.mapping,
        DPIF_R2_KEY_REPORT_MAPPING.round_id: DPIF_R2_KEY_REPORT_MAPPING.mapping,
        COF_EOI_KEY_REPORT_MAPPING.round_id: COF_EOI_KEY_REPORT_MAPPING.mapping,
        COF25_EOI_KEY_REPORT_MAPPING.round_id: COF25_EOI_KEY_REPORT_MAPPING.mapping,
        COF_R2_KEY_REPORT_MAPPING.round_id: COF_R2_KEY_REPORT_MAPPING.mapping,
        COF_R3W2_KEY_REPORT_MAPPING.round_id: COF_R3W2_KEY_REPORT_MAPPING.mapping,
        **({key: COF_KEY_REPORT_MAPPING.mapping for key in COF_KEY_REPORT_MAPPING.round_id}),
    },
)


def get_report_mapping_for_round(round_id):
    return ROUND_ID_TO_KEY_REPORT_MAPPING[round_id]
