from typing import Any

import tempfile
import aiohttp
import backoff
import asyncio
import io
import soundfile as sf
import sounddevice as sd

import global_value as g
from sound_helper import play_wav_from_memory, get_sound_device_id


async def _request_voice_base(suffix_param: str) -> aiohttp.ClientResponse:
    configAS = g.config["assistantSeika"]
    url = f"http://{configAS['name']}:{configAS['port']}/{suffix_param}"
    auth = aiohttp.BasicAuth(login=configAS["login"], password=configAS["password"])
    async with aiohttp.ClientSession() as session:
        async with session.get(url, auth=auth) as response:
            response.raise_for_status()
            return response


async def _request_voice_base_post(suffix_param: str) -> aiohttp.ClientResponse:
    configAS = g.config["assistantSeika"]
    url = f"http://{configAS['name']}:{configAS['port']}/{suffix_param}"
    auth = aiohttp.BasicAuth(login=configAS["login"], password=configAS["password"])
    async with aiohttp.ClientSession() as session:
        async with session.post(url, auth=auth) as response:
            response.raise_for_status()
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
        cmd = "EFFECT"
        suffix_param = f"{cmd}/{cid}/{param}/{value}"
        await _request_voice_base(suffix_param)
    except Exception as e:
        print(e)


async def talk_voice(text: str, cid: int = 0, sound_device_id: int = 0) -> None:
#    try:
#        configAS = g.config["assistantSeika"]
#        defaultCid = configAS["defaultCid"]
#        if not defaultCid:
#            # デフォルトが無効なら処理しない
#            return
#        if cid == 0:
#            cid = defaultCid
#        if sound_device_id == 0:
#            sound_device_id = get_sound_device_id(configAS["soundDeviceName"])
#        cmd = "SAVE2"
#        suffix_param = f"{cmd}/{cid}/{text}"
#        response = await _request_voice_base(suffix_param)
#        with tempfile.TemporaryFile(mode='wb') as f:
#            async for chunk in response.content.iter_any():
#                if not chunk:
#                    break
#                f.write(chunk)
#            play_wav_from_memory(f, sound_device_id)
#    except Exception as e:
#        print(e)
    configAS = g.config["assistantSeika"]
    cmd = "SAVE2"
    url = f"http://{configAS['name']}:{configAS['port']}/{cmd}/{cid}/{text}"
    auth = aiohttp.BasicAuth(login=configAS["login"], password=configAS["password"])
    await fetch_and_play_audio(url, auth, sound_device_id)


@backoff.on_exception(backoff.expo,
                      (aiohttp.ClientError, asyncio.TimeoutError),
                      max_tries=3)
async def fetch_and_play_audio(url, auth, sound_device_id):
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session: # セッション全体のタイムアウトを長めに設定
            async with session.get(url, auth=auth) as response:
                response.raise_for_status()
                if response.content_type != "audio/wav":
                    raise ValueError(f"Content-Type is not audio/wav: {response.content_type}")

                wav_bytes = bytearray()
                async for chunk in response.content.iter_chunked(8192): # チャンクサイズを指定
                    wav_bytes.extend(chunk)

                with io.BytesIO(wav_bytes) as wav_file:
                    data, samplerate = sf.read(wav_file)
                    sd.play(data, samplerate, device=sound_device_id)
                    sd.wait()

                print("再生完了")

    except (aiohttp.ClientError, asyncio.TimeoutError) as e:
        print(f"Request failed: {e}")
        raise # リトライ処理のために例外を再raise
    except ValueError as e:
        print(f"Invalid data error: {e}")
    except sf.SoundFileError as e:
        print(f"SoundFile error: {e}")
    except sd.PortAudioError as e:
        print(f"PortAudio error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
