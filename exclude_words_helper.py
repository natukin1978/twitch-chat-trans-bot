import re
import unicodedata

from text_helper import read_text_set


def read_exclude_words(name: str = "exclude_words.txt") -> list[str]:
    return list(read_text_set(name))


def match_exclude_word(exclude_words: list[str], target: str) -> bool:
    normalize_target = unicodedata.normalize("NFKC", target.strip())
    for exclude_word in exclude_words:
        if re.fullmatch(exclude_word, normalize_target, re.IGNORECASE):
            return True
    return False
