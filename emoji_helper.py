from typing import List

import twitchio
from emoji import distinct_emoji_list

from emote_helper import add_emotes, remove_emote


def add_emoji(emotes: List[str], text: str) -> None:
    emotes.extend(distinct_emoji_list(text))


def get_text_without_emojis(msg: twitchio.Message) -> str:
    emotes = []
    add_emotes(emotes, msg)
    add_emoji(emotes, msg.content)
    return remove_emote(msg.content, emotes)
