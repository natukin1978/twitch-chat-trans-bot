import re
import unicodedata

from config_helper import read_config


def read_replace_words(name: str = "replace_words.json"):
    return read_config(name)


def match_replace_word(replace_words: list[dict], target: str) -> str:
    """
    指定された置換ルールのリストに基づき、文字列内の該当部分を置き換えます。

    Args:
        replace_words (list[dict]): "from" と "to" のキーを持つ辞書のリスト
        target (str): 置換対象の文字列

    Returns:
        str: 置換後の文字列
    """
    # 判定用に文字表記の表記揺れ（全角・半角など）を正規化します
    normalized_text = unicodedata.normalize("NFKC", target.strip())

    # ルールを順番に適用して置換していきます
    for replace_word in replace_words:
        pattern = replace_word["from"]
        replacement = replace_word["to"]

        # re.sub(検索パターン, 置換後の文字列, 対象テキスト, フラグ)
        # 部分一致した箇所を指定の文字列に置き換えます
        normalized_text = re.sub(pattern, replacement, normalized_text, flags=re.IGNORECASE)

    return normalized_text
