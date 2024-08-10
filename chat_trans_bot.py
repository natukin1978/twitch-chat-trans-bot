import asyncio
import json

import aiohttp
import langdetect
import twitchio
import global_value as g
from twitchio.ext import commands

from config_helper import readConfig
from emoji_helper import get_text_without_emoji

# from talk_voice import talk_voice

g.config = readConfig()


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


class Bot(commands.Bot):
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

        user = msg.author.display_name

        text = get_text_without_emoji(msg)
        if not text:
            return

        result_langdetect = langdetect.detect(text)
        if result_langdetect == g.config["translate_gas"]["target"]:
            # await talk_voice(text, 50191)
            return

        translated_text = await translate_gas(text, g.config["translate_gas"]["target"])
        if not translated_text or text == translated_text:
            return

        # await talk_voice(translated_text, 50191)
        await msg.channel.send(f"{translated_text} [by {user}]")


async def main():
    bot = Bot()
    await bot.start()


if __name__ == "__main__":
    asyncio.run(main())
