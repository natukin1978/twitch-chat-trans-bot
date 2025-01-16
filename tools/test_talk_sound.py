import asyncio
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import global_value as g
from config_helper import readConfig
from sound_helper import get_sound_device
from talk_voice import talk_voice


def to_int(s):
    try:
        return int(s, 10)
    except ValueError:
        return False


args = len(sys.argv)
if args <= 2:
    exit(1)

text = sys.argv[1]
cid = int(sys.argv[2])
sound_device = "-1"
if args > 3:
    sound_device = sys.argv[3]

g.config = readConfig()

sound_device_id = to_int(sound_device)
if sound_device_id == False:
    sound_device_id, sound_device_name = get_sound_device(sound_device)
    print(f"{sound_device_id}: {sound_device_name}")


async def main():
    await talk_voice(text, cid, sound_device_id)


if __name__ == "__main__":
    asyncio.run(main())
