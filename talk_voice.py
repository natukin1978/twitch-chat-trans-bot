import logging

import aiohttp

import global_value as g

logger = logging.getLogger(__name__)


def get_basic_auth():
    configAS = g.config["assistantSeika"]
    return aiohttp.BasicAuth(login=configAS["login"], password=configAS["password"])


def get_base_url() -> str:
    configAS = g.config["assistantSeika"]
    return f"http://{configAS['name']}:{configAS['port']}"


async def set_voice_effect(param: str, value: any, cid: int = 0):
    try:
        configAS = g.config["assistantSeika"]
        defaultCid = configAS["defaultCid"]
        if not defaultCid:
            # デフォルトが無効なら処理しない
            return
        if cid == 0:
            cid = defaultCid
        url = get_base_url() + f"/EFFECT/{cid}/{param}/{value}"
        auth = get_basic_auth()
        async with aiohttp.ClientSession() as session:
            async with session.get(url, auth=auth) as response:
                return await response
    except Exception as e:
        logger.error("Error! set_voice_effect {e}")


async def talk_voice(text: str, cid: int = 0):
    try:
        configAS = g.config["assistantSeika"]
        defaultCid = configAS["defaultCid"]
        if not defaultCid:
            # デフォルトが無効なら処理しない
            return
        if cid == 0:
            cid = defaultCid
        if configAS["playAsync"]:
            cmd = "PLAYASYNC2"
        else:
            cmd = "PLAY2"
        url = get_base_url() + f"/{cmd}/{cid}"
        auth = get_basic_auth()
        params = {
            "talktext": text,
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, auth=auth, params=params) as response:
                return await response
    except Exception as e:
        logger.error("Error! talk_voice {e}")
