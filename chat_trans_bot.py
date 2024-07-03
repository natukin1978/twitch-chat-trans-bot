import aiohttp
import asyncio
import langdetect
import twitchio
import json
from twitchio.ext import commands
from config_helper import readConfig

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
        result_langdetect = langdetect.detect(text)
        if result_langdetect == GAS_TARGET:
            return

        translated_text = await translate_gas(text, GAS_TARGET)
        if not translated_text or text == translated_text:
            return

        user = msg.author.display_name
        await msg.channel.send(f"{translated_text} [by {user}]")


async def main():
    bot = Bot()
    await bot.start()


if __name__ == "__main__":
    asyncio.run(main())
