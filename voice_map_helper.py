import os
from typing import Any, Dict

import global_value as g
from csv_helper import read_csv_to_list


def read_voice_map() -> Dict[str, Any]:
    items = read_csv_to_list("voice_map.csv")
    result = {}
    for item in items:
        result[item[0]] = item[1:]
    return result


def get_cid(displayName: str) -> int:
    voice_map = read_voice_map()
    voice = voice_map.get(displayName, None)
    if not voice:
        return 0
    return voice[0]
