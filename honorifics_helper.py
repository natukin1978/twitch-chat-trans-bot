from config_helper import read_config


def read_honorifics(name: str = "honorifics.json"):
    return read_config(name)

def get_honorifics_default(honorifics) -> str:
    return honorifics["default"]

def get_honorifics_others(honorifics) -> list[str]:
    result = honorifics["other"]
    result.append(get_honorifics_default(honorifics))
    return result

def add_honorifics(honorifics, nickname: str) -> str:
    if not next(filter(lambda x: nickname.endswith(x), get_honorifics_others(honorifics)), None):
        nickname += get_honorifics_default(honorifics)
    return nickname
