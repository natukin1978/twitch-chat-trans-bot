import asyncio
import json

import aiohttp
import langdetect
import twitchio
import global_value as g
from twitchio.ext import commands

from config_helper import readConfig
from emoji_helper import get_text_without_emojis
from voice_map_helper import read_voice_map, get_cid
from talk_voice import talk_voice, set_voice_effect
from one_comme_users import read_one_comme_users, get_nickname

g.config = readConfig()

g.voice_map = read_voice_map()
g.one_comme_users = read_one_comme_users()
g.called_set_all_voice_effect = False


def get_use_nickname(displayName: str) -> str:
    nickname = get_nickname(displayName)
    if not nickname:
        nickname = displayName
    configH = g.config["honorifics"]
    if not next(filter(lambda x: nickname.endswith(x), configH["other"]), None):
        nickname += configH["default"]
    return nickname


async def translate_gas(text: str, target: str) -> str:
    try:
        param = {
            "text": text,
            "target": target,
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(
                g.config["translate_gas"]["url"], params=param
            ) as response:
                result = await response.json()
                return result["text"]
    except Exception as e:
        print(e)
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

        if msg.content.startswith("!"):
            await self.handle_commands(msg)
            return

        text = get_text_without_emojis(msg)
        user = msg.author.display_name
        cid = get_cid(user)
        nickname = get_use_nickname(user)

        if not g.called_set_all_voice_effect:
            # 1回だけ
            await set_all_voice_effect()
            g.called_set_all_voice_effect = True

        if not text:
            # 本文が無い場合でも名前だけは読み上げる
            await talk_voice(nickname, cid)
            return

        if self.prev_nickname == nickname:
            nickname = ""
        else:
            self.prev_nickname = nickname

        result_langdetect = langdetect.detect(text)
        if result_langdetect == g.config["translate"]["target"]:
            await talk_voice_with_nickname(nickname, text, cid)
            return

        translated_text = await translate_gas(text, g.config["translate"]["target"])
        if not translated_text or text == translated_text:
            return

        await talk_voice_with_nickname(nickname, translated_text, cid)
        await msg.channel.send(f"{translated_text} [by {user}]")


async def main():
    bot = Bot()
    await bot.start()


if __name__ == "__main__":
    asyncio.run(main())
