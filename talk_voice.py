from typing import Any

import aiohttp

import global_value as g
from sound_helper import get_sound_device, play_wav_from_memory


def get_url_auth(suffix_param: str) -> tuple[str, aiohttp.BasicAuth]:
    configAS = g.config["assistantSeika"]
    url = f"http://{configAS['name']}:{configAS['port']}/{suffix_param}"
    auth = aiohttp.BasicAuth(login=configAS["login"], password=configAS["password"])
    return url, auth


async def set_voice_effect(param: str, value: Any, cid: int = 0) -> None:
    try:
        configAS = g.config["assistantSeika"]
        defaultCid = configAS["defaultCid"]
        if not defaultCid:
            # デフォルトが無効なら処理しない
            return
        if cid == 0:
            cid = defaultCid
        cmd = "EFFECT"
        suffix_param = f"{cmd}/{cid}/{param}/{value}"
        url, auth = get_url_auth(suffix_param)
        async with aiohttp.ClientSession() as session:
            async with session.get(url, auth=auth) as response:
                return response
    except aiohttp.ClientError as e:
        print(f"Request failed: {e}")
    except ValueError as e:
        print(f"Invalid data error: {e}")
    except Exception as e:
        print(e)


async def talk_voice(text: str, cid: int = 0, sound_device_id: int = -1) -> None:
    try:
        configAS = g.config["assistantSeika"]
        defaultCid = configAS["defaultCid"]
        if not defaultCid:
            # デフォルトが無効なら処理しない
            return
        if cid == 0:
            cid = defaultCid
        if sound_device_id == -1:
            sound_device_id, _ = get_sound_device(configAS["soundDeviceName"])
        cmd = "SAVE2"
        suffix_param = f"{cmd}/{cid}/{text}"
        url, auth = get_url_auth(suffix_param)
        async with aiohttp.ClientSession() as session:
            async with session.get(url, auth=auth) as response:
                response.raise_for_status()
                if response.content_type != "audio/wav":
                    raise ValueError(
                        f"Content-Type is not audio/wav: {response.content_type}"
                    )

                wav_bytes = bytearray()
                async for chunk in response.content.iter_chunked(65535):
                    wav_bytes.extend(chunk)

                wait = not configAS["playAsync"]
                play_wav_from_memory(wav_bytes, sound_device_id, wait)

    except aiohttp.ClientError as e:
        print(f"Request failed: {e}")
    except ValueError as e:
        print(f"Invalid data error: {e}")
    except Exception as e:
        print(e)
