from typing import Any

import prance

from config import Config


def get_bundled_specs(main_file: str) -> dict[str, Any]:
    path_string = Config.FLASK_ROOT + main_file
    parser = prance.ResolvingParser(path_string, strict=False)
    parser.parse()
    return parser.specification
