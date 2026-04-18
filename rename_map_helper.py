from config_helper import read_config


def read_rename_map(name: str = "rename_map.json"):
    result = read_config(name)
    if not result:
        return []
    return result


def get_nickname(rename_map, displayName: str) -> str | None:
    rename = next(filter(lambda x: x["from"] == displayName, rename_map), None)
    if rename is None:
        return None
    return rename["to"]
