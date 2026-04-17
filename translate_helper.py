import logging
import random

import aiohttp

import global_value as g
from one_comme_users import OneCommeUsers
from rename_map_helper import read_rename_map
from talk_voice import talk_voice

logger = logging.getLogger(__name__)

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
    # 必要なら敬称を付加する
    configH = g.config["honorifics"]
    if not next(filter(lambda x: nickname.endswith(x), configH["other"]), None):
        nickname += configH["default"]
    return nickname


def get_random_value() -> str:
    service = g.config["translate"]["service"]
    if service == "deepL":
        values = g.config["deepL"]["apiKey"]
    if service == "translateGas":
        values = g.config["translateGas"]["url"]
    i = random.randrange(len(values))
    return values[i]


async def translate_deepL(text: str, target: str) -> str:
    try:
        headers = {
            "Authorization": "DeepL-Auth-Key " + get_random_value(),
            "Content-Type": "application/json",
        }
        data = {
            "text": [text],
            "target_lang": target,
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(
                g.config["deepL"]["endpoint"], headers=headers, json=data
            ) as response:
                result = await response.json()
                return result["translations"][0]["text"]
    except Exception as e:
        logger.error(e)
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
        logger.error(e)
        return ""


async def translate(text: str, target: str) -> str:
    service = g.config["translate"]["service"]
    if service == "deepL":
        return await translate_deepL(text, target)
    if service == "translateGas":
        return await translate_gas(text, target)
    return ""


async def talk_voice_with_nickname(nickname: str, text: str, cid: int) -> None:
    value = text
    if not nickname:
        value = text
    else:
        value = nickname + " " + text
    await talk_voice(value, cid)
