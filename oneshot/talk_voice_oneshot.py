import asyncio
import logging
import os
import sys

args = len(sys.argv)
if args <= 2:
    exit(1)

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
    text = sys.argv[1]
    cid = int(sys.argv[2])
    await talk_voice(text, cid)

if __name__ == "__main__":
    asyncio.run(main())
