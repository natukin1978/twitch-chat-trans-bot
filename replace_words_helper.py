import re
import unicodedata

from csv_helper import read_csv_to_list


def read_replace_words(name: str = "replace_words.csv") -> list[list[any]]:
    return read_csv_to_list(name)


def match_replace_word(replace_words: list[list[any]], target: str) -> str:
    normalize_target = unicodedata.normalize("NFKC", target.strip())
    for replace_word in replace_words:
        if re.fullmatch(replace_word[0], normalize_target, re.IGNORECASE):
            return replace_word[1]
    return target
