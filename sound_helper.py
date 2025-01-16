import io

import sounddevice as sd
import soundfile as sf


def get_sound_device(sound_device_name: str) -> tuple[int, str]:
    if not sound_device_name:
        return (-1, "Default")
    devices = sd.query_devices()
    for i, device in enumerate(devices):
        hostapi = sd.query_hostapis(device["hostapi"])
        full_name = f'{device["name"]}, {hostapi["name"]}'
        if sound_device_name in full_name:
            return (i, full_name)
    return (-1, "Not found")


def play_wav_from_memory(wav_bytes, sound_device_id: int, wait: bool):
    """メモリバッファのWAVデータを再生する"""
    try:
        with io.BytesIO(wav_bytes) as wav_file:
            data, samplerate = sf.read(wav_file)
            if sound_device_id < 0:
                sd.play(data, samplerate)
            else:
                sd.play(data, samplerate, device=sound_device_id)
            if wait:
                sd.wait()
    except sf.SoundFileError as e:
        print(f"Error: WAVデータの読み込みに失敗しました: {e}")
    except sd.PortAudioError as e:
        print(f"Error: 再生中にエラーが発生しました: {e}")
    except Exception as e:
        print(f"Error: 予期せぬエラーが発生しました: {e}")
