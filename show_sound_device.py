import sounddevice as sd


def list_devices():
    """利用可能なオーディオデバイスをリスト表示する"""
    devices = sd.query_devices()
    print(devices)


if __name__ == "__main__":
    list_devices()  # デバイスリストを表示
