import os
from typing import Any, Dict

import global_value as g
from csv_helper import read_csv_to_list


def read_voice_map() -> Dict[str, Any]:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(current_dir, "voice_map.csv")
    items = read_csv_to_list(path)
    result = {}
    for item in items:
        result[item[0]] = item[1:]
    return result


def get_cid(displayName: str) -> int:
    voice = g.voice_map.get(displayName, None)
    if not voice:
        return 0
    return voice[0]


def get_sound_device_name(displayName: str) -> str:
    voice = g.voice_map.get(displayName, None)
    if not voice:
        return 0
    return voice[1]
