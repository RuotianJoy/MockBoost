import os
import sounddevice as sd
import numpy as np
import vosk
import json
import sys

class VoskRecognizer:
    def __init__(self, model_path="Model", sample_rate=8000):
        self.model_path = model_path
        self.sample_rate = sample_rate
        self.model = None
        self.recognizer = None
        self._load_model()

    def _load_model(self):
        if not os.path.exists(self.model_path):
            print("模型路径不存在，请下载模型并放置到该目录")
            exit(1)

        self.model = vosk.Model(self.model_path)
        self.recognizer = vosk.KaldiRecognizer(self.model, self.sample_rate)

    def recognize_speech(self):
        print("请开始说话...")

        with sd.RawInputStream(samplerate=self.sample_rate, channels=1, dtype='int16', blocksize=4096, callback=self._callback):
            while True:
                pass  # 持续监听音频

    def _callback(self, indata, frames, time, status):
        if status:
            print(status, file=sys.stderr)

        # 将 _cffi_backend.buffer 对象转换为 bytes 类型
        indata_bytes = memoryview(indata).tobytes()

        if self.recognizer.AcceptWaveform(indata_bytes):  # 处理音频数据
            result = self.recognizer.Result()
            print("识别结果：", json.loads(result)["text"])  # 输出文本
        else:
            partial_result = self.recognizer.PartialResult()
            print("部分识别：", json.loads(partial_result)["partial"])

if __name__ == "__main__":
    recognizer = VoskRecognizer()
    recognizer.recognize_speech()
