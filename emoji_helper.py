import twitchio
from emoji import distinct_emoji_list
from typing import List


def get_emotes(msg: twitchio.Message) -> List[str]:
    if not msg.tags:
        return []

    mt_emotes = msg.tags["emotes"]
    if not mt_emotes:
        return []

    emotes = mt_emotes.split("/")
    result = []
    for emote in emotes:
        _, e_pos = emote.split(":")
        ed_pos = None
        if "," in e_pos:
            # 同一エモートが複数使われてたら，その数分，情報が入ってくる
            # （例：1110537:4-14,16-26）
            ed_pos = e_pos.split(",")
        else:
            ed_pos = [e_pos]
        for e in ed_pos:
            e_s, e_e = e.split("-")
            result.append(msg.content[int(e_s) : int(e_e) + 1])

    return result


def remove_emoji(text: str, emotes: List[str]) -> str:
    emojis = distinct_emoji_list(text)
    for emoji in emojis:
        emotes.append(emoji)

    emotes = list(set(emotes))
    emotes.sort(key=len, reverse=True)
    for emote in emotes:
        text = text.replace(emote, "")

    text = text.strip()
    return text


def get_text_without_emoji(msg: twitchio.Message) -> str:
    emotes = get_emotes(msg)
    return remove_emoji(msg.content, emotes)
