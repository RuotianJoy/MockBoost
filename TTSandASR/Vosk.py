import os
import sounddevice as sd
import numpy as np
import vosk
import json
import sys

class VoskRecognizer:
    # 单例实例
    _instance = None
    _initialized = False
    def __new__(cls, model_path="D:\\Project\\MockBoost\\TTSandASR\\Model", sample_rate=8000):
        # 如果单例实例不存在，则创建一个
        if cls._instance is None:
            cls._instance = super(VoskRecognizer, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
        
    def __init__(self, model_path="D:\\Project\\MockBoost\\TTSandASR\\Model", sample_rate=8000):
        # 只在第一次初始化时加载模型
        if not self._initialized:
            self.model_path = model_path
            self.sample_rate = sample_rate
            self.model = None
            self.recognizer = None
            self._load_model()
            VoskRecognizer._initialized = True

    def _load_model(self):
        if not os.path.exists(self.model_path):
            print("模型路径不存在，请下载模型并放置到该目录")
            exit(1)

        self.model = vosk.Model(self.model_path)
        self.recognizer = vosk.KaldiRecognizer(self.model, self.sample_rate)

    def recognize_speech(self, callback=None, max_duration=50000):
        """
        执行语音识别并返回识别结果
        
        Args:
            callback: 可选的回调函数，用于实时接收识别结果
            max_duration: 最大监听时间(毫秒)
        
        Returns:
            str: 识别到的文本
        """
        print("请开始说话...")
        result_text = ""
        
        def audio_callback(indata, frames, time, status):
            nonlocal result_text
            if status:
                print(status, file=sys.stderr)

            # 将 _cffi_backend.buffer 对象转换为 bytes 类型
            indata_bytes = memoryview(indata).tobytes()

            if self.recognizer.AcceptWaveform(indata_bytes):  # 处理音频数据
                result = self.recognizer.Result()
                result_text = json.loads(result)["text"]
                print("识别结果：", result_text)  # 输出文本
                
                # 如果提供了回调函数，立即调用回调函数
                if callback and result_text.strip():
                    callback(result_text)
                
                if result_text.strip():  # 如果结果不为空，则停止监听
                    raise sd.CallbackStop()
            else:
                partial_result = self.recognizer.PartialResult()
                partial_text = json.loads(partial_result)["partial"]
                print("部分识别：", partial_text)
                
                # 如果提供了回调函数，也可以传递部分识别结果
                if callback and partial_text.strip():
                    callback(partial_text, is_final=False)
        
        try:
            with sd.RawInputStream(samplerate=self.sample_rate, channels=1, dtype='int16', blocksize=4096, callback=audio_callback):
                sd.sleep(int(max_duration))  # 最多监听指定时间，可以根据需要调整
        except sd.CallbackStop:
            pass  # 正常停止，不需要处理
        
        return result_text  # 返回识别结果

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

def recognize_speech_once(model_path="D:\\Project\\MockBoost\\TTSandASR\\Model", sample_rate=8000, max_duration=10000, callback=None):
    """
    执行一次语音识别并返回识别结果
    
    Args:
        model_path: Vosk模型路径
        sample_rate: 采样率
        max_duration: 最大监听时间(毫秒)
        callback: 可选的回调函数，用于实时接收识别结果
    
    Returns:
        str: 识别到的文本
    """
    # 使用单例模式，避免重复初始化模型
    recognizer = VoskRecognizer(model_path, sample_rate)
    return recognizer.recognize_speech(callback=callback, max_duration=max_duration)


if __name__ == "__main__":
    recognizer = VoskRecognizer()
    recognizer.recognize_speech()
