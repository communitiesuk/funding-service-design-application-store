from collections import defaultdict

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
from config.key_report_mappings.cof_r4_key_report_mapping import (
    COF_R4_KEY_REPORT_MAPPING,
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
    COF_KEY_REPORT_MAPPING,
    CYP_R1_KEY_REPORT_MAPPING,
    DPIF_R2_KEY_REPORT_MAPPING,
    COF_EOI_KEY_REPORT_MAPPING,
    COF_R4_KEY_REPORT_MAPPING,
)

ROUND_ID_TO_KEY_REPORT_MAPPING = defaultdict(
    # default COF R2 as at the time of this refactor, that was used by default in existing code
    lambda: COF_R2_KEY_REPORT_MAPPING.mapping,
    {m.round_id: m.mapping for m in MAPPINGS},
)


def get_report_mapping_for_round(round_id):
    return ROUND_ID_TO_KEY_REPORT_MAPPING[round_id]
