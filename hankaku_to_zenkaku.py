import unicodedata

# 半角記号を全角記号に変換する変換テーブル
HANKAKU_TO_ZENKAKU_MAP = {
    ord("&"): "＆",
    ord("+"): "＋",
    ord("<"): "＜",
    ord("="): "＝",
    ord(">"): "＞",
    ord("@"): "＠",
    ord("^"): "＾",
    ord("_"): "＿",
    ord("`"): "｀",
    ord("|"): "｜",
    ord("~"): "～",
    ord("!"): "！",
    ord("#"): "＃",
    ord("$"): "＄",
    ord(","): "，",
    ord("%"): "％",
    ord("."): "．",
    ord("'"): "’",
    ord("("): "（",
    ord(")"): "）",
    ord("-"): "－",
    ord(" "): "　",  # 半角スペースを全角スペースに変換
}


def hankaku_to_zenkaku_symbols(text):
    """半角記号を全角記号に変換する関数"""
    return text.translate(HANKAKU_TO_ZENKAKU_MAP)
