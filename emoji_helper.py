import twitchio
from emoji import distinct_emoji_list
from typing import List


def add_emotes(emotes: List[str], msg: twitchio.Message) -> None:
    if not msg.tags:
        return []

    mt_emotes = msg.tags["emotes"]
    if not mt_emotes:
        return []

    mt_emotes_split = mt_emotes.split("/")
    for emote in mt_emotes_split:
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
            emotes.append(msg.content[int(e_s) : int(e_e) + 1])


def add_emoji(emotes: List[str], text: str) -> None:
    emotes.extend(distinct_emoji_list(text))


def remove_emoji(text: str, emotes: List[str]) -> str:
    emotes = list(set(emotes))
    emotes.sort(key=len, reverse=True)
    for emote in emotes:
        text = text.replace(emote, "")

    text = text.strip()
    return text


def get_text_without_emojis(msg: twitchio.Message) -> str:
    emotes = []
    add_emotes(emotes, msg)
    add_emoji(emotes, msg.content)
    return remove_emoji(msg.content, emotes)
