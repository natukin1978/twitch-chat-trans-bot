import asyncio
import logging
import os
import sys

import asqlite

import constants
import global_value as g
from config_helper import read_config
from logging_setup import setup_app_logging

g.app_name = "twitch_chat_trans_bot"
g.base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
g.config = read_config()

# ロガーの設定
setup_app_logging(g.config["logLevel"], log_file_path=f"{g.app_name}.log")
logger = logging.getLogger(__name__)

from twitch_bot import (
    TwitchBot,
    setup_database,
)

configH = g.config["honorifics"]
configH["other"].append(configH["default"])


async def main():
    # conduit_id の警告を抑止したい…
    logging.getLogger("twitchio.client").setLevel(logging.ERROR)
    # StarletteAdapter の警告を抑止したい…
    logging.getLogger("twitchio.web.aio_adapter").setLevel(logging.ERROR)

    bot = None
    async with asqlite.create_pool("tokens.db") as tdb:
        tokens, subs = await setup_database(tdb)

        bot = TwitchBot(token_database=tdb, subs=subs)
        for pair in tokens:
            await bot.add_token(*pair)

        if not tokens:
            print("")
            print("※ Twitch認証が必要な場合")
            print("")
            print("Webブラウザで以下に表示されているアドレスにアクセスしてください。")
            print("")
            print("TwitchのBOTアカウントでログインして「許可」してください。")
            print(constants.CALLBACK_URL_BOT)
            print("")
            print("Twitchの配信チャンネルアカウントでログインして「許可」してください。")
            print(constants.CALLBACK_URL_OWNER)
            print("")

        await bot.start(load_tokens=False)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    finally:
        pass
