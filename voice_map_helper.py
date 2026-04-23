from config_helper import read_config


def read_voice_map(name: str = "voice_map.json"):
    result = read_config(name)
    if not result:
        return []
    return result


def get_cid(voice_map, displayName: str) -> int:
    voice = next(filter(lambda x: x["name"] == displayName, voice_map), None)
    if voice is None:
        return 0
    return voice["cid"]
