import aiohttp

from typing import Any
import global_value as g


async def _request_voice_base(suffix_param: str) -> aiohttp.ClientResponse:
    configAS = g.config["assistantSeika"]
    url = f"http://{configAS['name']}:{configAS['port']}/{suffix_param}"
    auth = aiohttp.BasicAuth(login=configAS["login"], password=configAS["password"])
    async with aiohttp.ClientSession() as session:
        async with session.get(url, auth=auth) as response:
            return response


async def set_voice_effect(param: str, value: Any, cid: int = 0) -> None:
    try:
        configAS = g.config["assistantSeika"]
        defaultCid = configAS["defaultCid"]
        if not defaultCid:
            # デフォルトが無効なら処理しない
            return
        if cid == 0:
            cid = defaultCid
        suffix_param = f"EFFECT/{cid}/{param}/{value}"
        await _request_voice_base(suffix_param)
    except Exception as e:
        print(e)


async def talk_voice(text: str, cid: int = 0) -> None:
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
        suffix_param = f"{cmd}/{cid}/{text}"
        await _request_voice_base(suffix_param)
    except Exception as e:
        print(e)
