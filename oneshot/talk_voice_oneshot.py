import asyncio
import logging
import os
import sys

sys.path.append("..")
sys.path.append(".")

import global_value as g

g.app_name = "talk_voice_oneshot"
g.base_dir = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), os.pardir))

from config_helper import read_config
from talk_voice import talk_voice

g.config = read_config()

# ロガーの設定
logging.basicConfig(level=logging.INFO)


async def main():
    await talk_voice("ナツキソ 読み上げない&のだ", 200001)


if __name__ == "__main__":
    asyncio.run(main())
