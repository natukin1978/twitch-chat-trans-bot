import re
import unicodedata

from config_helper import read_config


def read_exclude_words(name: str = "exclude_words.json"):
    result = read_config(name)
    if not result:
        return []
    return result


def match_exclude_word(exclude_words, target: str) -> bool:
    normalize_target = unicodedata.normalize("NFKC", target.strip())
    for exclude_word in exclude_words:
        if re.fullmatch(exclude_word, normalize_target, re.IGNORECASE):
            return True
    return False
