from collections import defaultdict

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

MAPPINGS = (
    COF_R2_KEY_REPORT_MAPPING,
    COF_R3W2_KEY_REPORT_MAPPING,
    CYP_R1_KEY_REPORT_MAPPING,
    DPIF_R2_KEY_REPORT_MAPPING,
)

ROUND_ID_TO_KEY_REPORT_MAPPING = defaultdict(
    # default COF R2 as at the time of this refactor, that was used by default in existing code
    lambda: COF_R2_KEY_REPORT_MAPPING.mapping,
    {m.round_id: m.mapping for m in MAPPINGS},
)


def get_report_mapping_for_round(round_id):
    if round_id == COF_R2_KEY_REPORT_MAPPING.round_id:
        return COF_R2_KEY_REPORT_MAPPING
    elif round_id == COF_R3W2_KEY_REPORT_MAPPING.round_id:
        return COF_R3W2_KEY_REPORT_MAPPING
    elif round_id == CYP_R1_KEY_REPORT_MAPPING.round_id:
        return CYP_R1_KEY_REPORT_MAPPING
    elif round_id == DPIF_R2_KEY_REPORT_MAPPING.round_id:
        return DPIF_R2_KEY_REPORT_MAPPING
