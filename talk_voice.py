import logging
import re

import aiohttp

import global_value as g
from config_helper import read_config

logger = logging.getLogger(__name__)


def get_voice_json():
    return read_config("voice.json")


def get_voice_map(voice_json, cid: int):
    try:
        cid_str = str(cid)
        voice_maps = voice_json["maps"]
        for voice_map in voice_maps:
            pattern = voice_map["cid"]
            if re.fullmatch(pattern, cid_str):
                return voice_map
        return None
    except:
        return None


def get_basic_auth():
    configAS = g.config["assistantSeika"]
    return aiohttp.BasicAuth(login=configAS["login"], password=configAS["password"])


def get_base_url() -> str:
    configAS = g.config["assistantSeika"]
    return f"http://{configAS['name']}:{configAS['port']}"


async def talk_voice(text: str, cid: int = 0):
    try:
        voice_json = get_voice_json()
        defaultCid = voice_json["defaultCid"]
        if not defaultCid:
            # デフォルトが無効なら処理しない
            return
        if cid == 0:
            cid = defaultCid
        if voice_json["playAsync"]:
            cmd = "PLAYASYNC2"
        else:
            cmd = "PLAY2"
        url = get_base_url() + f"/{cmd}/{cid}"
        auth = get_basic_auth()
        effects = voice_json["effects"]
        voice_map = get_voice_map(voice_json, cid)
        if voice_map:
            effects |= voice_map["effects"]
        request_body = {
            "talktext": text,
            "effects": effects,
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, auth=auth, json=request_body) as response:
                return response
    except Exception as e:
        logger.error(f"Error! talk_voice {e}")
