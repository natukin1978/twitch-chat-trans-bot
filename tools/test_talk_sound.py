import asyncio
import sys

import global_value as g
from config_helper import readConfig
from talk_voice import talk_voice

args = len(sys.argv)
if args <= 3:
    exit(1)
text = sys.argv[1]
cid = int(sys.argv[2])
sound_device_id = int(sys.argv[3])

g.config = readConfig()


async def main():
    await talk_voice(text, cid, sound_device_id)


if __name__ == "__main__":
    asyncio.run(main())
