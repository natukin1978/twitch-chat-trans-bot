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
from rename_map_helper import read_rename_map
from replace_words_helper import match_replace_word, read_replace_words
from talk_voice import talk_voice
from voice_map_helper import get_cid

g.config = read_config()

# ロガーの設定
logging.basicConfig(level=logging.INFO)


def get_use_nickname(displayName: str) -> str:
    # ニックネームの優先度は rename_map.csv > わんコメCSV
    nickname = None
    rename_map = read_rename_map()
    if rename_map:
        rename = rename_map.get(displayName, None)
        if rename is not None:
            nickname = rename[0]
            if not nickname:
                return ""

    if nickname is None:
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

        if not text:
            # 本文が無い場合でも名前だけは読み上げる
            await talk_voice(nickname, cid)
            return

        if self.prev_nickname == nickname:
            # 直前と同じ人の名前は省略する
            nickname = ""
        else:
            self.prev_nickname = nickname

        replace_words = read_replace_words()
        text = match_replace_word(replace_words, text)

        exclude_words = read_exclude_words()
        if match_exclude_word(exclude_words, text):
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
