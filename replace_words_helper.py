import re
import unicodedata

from config_helper import read_config


def read_replace_words(name: str = "replace_words.json"):
    return read_config(name)


def match_replace_word(replace_words, target: str) -> str:
    normalize_target = unicodedata.normalize("NFKC", target.strip())
    for replace_word in replace_words:
        if re.fullmatch(replace_word["from"], normalize_target, re.IGNORECASE):
            return replace_word["to"]
    return target
