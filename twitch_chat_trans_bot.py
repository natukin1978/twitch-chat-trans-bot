import asyncio
import json
import logging
import os
import random
import re
import sys

import aiohttp
import langdetect
import twitchio
from twitchio.ext import commands

import global_value as g

g.app_name = "twitch_chat_trans_bot"
g.base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))

from config_helper import read_config
from emoji_helper import get_text_without_emojis
from exclude_words_helper import match_exclude_word, read_exclude_words
from one_comme_users import OneCommeUsers
from talk_voice import set_voice_effect, talk_voice
from voice_map_helper import get_cid, read_voice_map

g.config = read_config()

# ロガーの設定
logging.basicConfig(level=logging.INFO)

g.voice_map = read_voice_map()
g.exclude_words = read_exclude_words()
g.one_comme_users = OneCommeUsers.read_one_comme_users()
g.called_set_all_voice_effect = False


def get_use_nickname(displayName: str) -> str:
    nickname = OneCommeUsers.get_nickname(displayName)
    if not nickname:
        nickname = displayName
    configH = g.config["honorifics"]
    if not next(filter(lambda x: nickname.endswith(x), configH["other"]), None):
        nickname += configH["default"]
    return nickname


def get_random_value() -> str:
    service = g.config["translate"]["service"]
    if service == "deepL":
        values = g.config["deepL"]["apiKey"]
    if service == "translate_gas":
        values = g.config["translate_gas"]["url"]
    i = random.randrange(len(values))
    return values[i]


async def translate_deepL(text: str, target: str) -> str:
    try:
        param = {
            "auth_key": get_random_value(),
            "text": text,
            "target_lang": target,
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(
                g.config["deepL"]["endpoint"], params=param
            ) as response:
                result = await response.json()
                return result["translations"][0]["text"]
    except Exception as e:
        print(e)
        return ""


async def translate_gas(text: str, target: str) -> str:
    try:
        param = {
            "text": text,
            "target": target,
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(get_random_value(), params=param) as response:
                result = await response.json()
                return result["text"]
    except Exception as e:
        print(e)
        return ""


async def translate(text: str, target: str) -> str:
    service = g.config["translate"]["service"]
    if service == "deepL":
        return await translate_deepL(text, target)
    if service == "translate_gas":
        return await translate_gas(text, target)
    return ""


async def set_all_voice_effect() -> None:
    configAS = g.config["assistantSeika"]
    set_cid = set()
    for value in g.voice_map.values():
        set_cid.add(value[0])
    set_cid.add(configAS["defaultCid"])
    for cid in set_cid:
        await set_voice_effect("speed", configAS["speed"], cid)
        await set_voice_effect("volume", configAS["volume"], cid)


async def talk_voice_with_nickname(nickname: str, text: str, cid: int) -> None:
    value = text
    if not nickname:
        value = text
    else:
        value = nickname + " " + text
    await talk_voice(value, cid)


class Bot(commands.Bot):
    prev_nickname = ""

    def __init__(self):
        super().__init__(
            token=g.config["twitch"]["accessToken"],
            prefix="!",
            initial_channels=[g.config["twitch"]["loginChannel"]],
        )

    async def event_message(self, msg: twitchio.Message):
        if msg.echo:
            return

        # コマンドかどうか調べる
        is_cmd = msg.content.startswith("!")

        text = get_text_without_emojis(msg)
        user = msg.author.display_name
        cid = get_cid(user)
        nickname = get_use_nickname(user)

        if is_cmd:
            text = Bot.get_cmd_value(text)

        if not g.called_set_all_voice_effect:
            # 1回だけ
            await set_all_voice_effect()
            g.called_set_all_voice_effect = True

        if not text:
            # 本文が無い場合でも名前だけは読み上げる
            await talk_voice(nickname, cid)
            return

        if self.prev_nickname == nickname:
            # 直前と同じ人の名前は省略する
            nickname = ""
        else:
            self.prev_nickname = nickname

        if match_exclude_word(g.exclude_words, text):
            # 除外キーワードなので翻訳しない
            await talk_voice_with_nickname(nickname, text, cid)
            return

        result_langdetect = langdetect.detect(text)
        if result_langdetect == g.config["translate"]["target"]:
            # 母国語と同じ
            await talk_voice_with_nickname(nickname, text, cid)
            return

        if is_cmd:
            # コマンドなら翻訳しない
            # 読み上げない
            return

        translated_text = await translate(text, g.config["translate"]["target"])
        if translated_text == text:
            # 翻訳前後が一致
            await talk_voice_with_nickname(nickname, text, cid)
            return

        if not translated_text:
            translated_text = text

        await talk_voice_with_nickname(nickname, translated_text, cid)
        await msg.channel.send(f"{translated_text} [by {user}]")

    @staticmethod
    def get_cmd_value(content: str) -> str:
        pattern = r"^![^ ]+ (.*?)$"
        match = re.search(pattern, content)
        if not match:
            logger.debug("Not match: " + content)
            return ""

        return match.group(1)


async def main():
    bot = Bot()
    await bot.start()


if __name__ == "__main__":
    asyncio.run(main())
