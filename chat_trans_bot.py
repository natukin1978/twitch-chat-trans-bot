import asyncio
import json
from typing import List

import aiohttp
import langdetect
import twitchio
from emoji import distinct_emoji_list
from twitchio.ext import commands

from config_helper import readConfig
# from talk_voice import talk_voice

config = readConfig()

# TwitchのOAuthトークン
ACCESS_TOKEN = config["twitch"]["accessToken"]
# Twitchチャンネルの名前
CHANNEL_NAME = config["twitch"]["loginChannel"]

GAS_TARGET = config["translate_gas"]["target"]
GAS_URL = config["translate_gas"]["url"]


async def translate_gas(text: str, target: str) -> str:
    try:
        param = {
            "text": text,
            "target": target,
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(GAS_URL, params=param) as response:
                result = await response.json()
                return result["text"]
    except Exception as e:
        print(e)
        return ""


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


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(
            token=ACCESS_TOKEN,
            prefix="!",
            initial_channels=[CHANNEL_NAME],
        )

    async def event_message(self, msg: twitchio.Message):
        if msg.echo:
            return

        if msg.content.startswith("!"):
            await self.handle_commands(msg)
            return

        text = msg.content
        user = msg.author.display_name

        emote_list = get_emotes(msg)

        emojis = distinct_emoji_list(text)
        for emoji in emojis:
            emote_list.append(emoji)

        emote_list = list(set(emote_list))
        emote_list.sort(key=len, reverse=True)
        for emote in emote_list:
            text = text.replace(emote, "")

        text = text.strip()
        if not text:
            return

        result_langdetect = langdetect.detect(text)
        if result_langdetect == GAS_TARGET:
            # await talk_voice(text, 50191)
            return

        translated_text = await translate_gas(text, GAS_TARGET)
        if not translated_text or text == translated_text:
            return

        # await talk_voice(translated_text, 50191)
        await msg.channel.send(f"{translated_text} [by {user}]")


async def main():
    bot = Bot()
    await bot.start()


if __name__ == "__main__":
    asyncio.run(main())
