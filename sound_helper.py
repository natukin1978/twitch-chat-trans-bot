import io

import sounddevice as sd
import soundfile as sf


def get_sound_device_id(sound_device_name: str):
    devices = sd.query_devices()
    for i, device in enumerate(devices):
        if device["name"] == sound_device_name:
            return i
    return 0


def play_wav_from_memory(wav_bytes, sound_device_id: int, wait: bool):
    """メモリバッファのWAVデータを再生する"""
    try:
        with io.BytesIO(wav_bytes) as wav_file:
            data, samplerate = sf.read(wav_file)
            sd.play(data, samplerate, device=sound_device_id)
            if wait:
                sd.wait()
    except sf.SoundFileError as e:
        print(f"Error: WAVデータの読み込みに失敗しました: {e}")
    except sd.PortAudioError as e:
        print(f"Error: 再生中にエラーが発生しました: {e}")
    except Exception as e:
        print(f"Error: 予期せぬエラーが発生しました: {e}")
