import os
import sounddevice as sd
import numpy as np
import vosk
import json
import sys
import logging
import json
# 配置日志记录
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# 创建文件处理器
file_handler = logging.FileHandler('vosk_recognition.log')
file_handler.setLevel(logging.INFO)

# 创建控制台处理器
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# 创建格式化器
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# 添加处理器到日志记录器
logger.addHandler(file_handler)
logger.addHandler(console_handler)

def get_resource_path(relative_path):
    """获取资源文件的绝对路径，兼容开发环境和打包环境"""
    try:
        # PyInstaller创建临时文件夹，将路径存储在_MEIPASS中
        base_path = sys._MEIPASS
    except Exception:
        # 不在打包环境中，使用当前文件的目录
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

class VoskRecognizer:
    # 单例实例
    _instance = None
    _initialized = False
    def __new__(cls, model_path=None, sample_rate=8000):
        logger.debug(f"Creating new VoskRecognizer instance with model_path: {model_path}")
        # 如果单例实例不存在，则创建一个
        if cls._instance is None:
            cls._instance = super(VoskRecognizer, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, model_path=None, sample_rate=8000):
        # 如果未指定模型路径，则使用默认路径
        if model_path is None:
            # 使用get_resource_path获取兼容打包环境的模型路径
            model_path = get_resource_path("Model")

        self.model_path = model_path
        logger.info(f"Using model path: {model_path}")
        self.sample_rate = sample_rate
        self.model = None
        self.recognizer = None
        self._load_model()

    def _load_model(self):
        if not os.path.exists(self.model_path):
            error_msg = f"模型路径不存在: {self.model_path}，请确保模型文件已正确打包"
            logger.error(error_msg)
            raise FileNotFoundError(f"Vosk model not found at {self.model_path}")

        logger.info("Loading Vosk model...")
        self.model = vosk.Model(self.model_path)
        self.recognizer = vosk.KaldiRecognizer(self.model, self.sample_rate)
        logger.info("Vosk model loaded successfully")

    def recognize_speech(self, callback=None, max_duration=50000):
        """
        执行语音识别并返回识别结果

        Args:
            callback: 可选的回调函数，用于实时接收识别结果
            max_duration: 最大监听时间(毫秒)

        Returns:
            str: 识别到的文本
        """
        logger.info("开始语音识别...")
        result_text = ""

        def audio_callback(indata, frames, time, status):
            nonlocal result_text
            if status:
                logger.error(f"音频输入错误: {status}")

            # 将 _cffi_backend.buffer 对象转换为 bytes 类型
            indata_bytes = memoryview(indata).tobytes()

            if self.recognizer.AcceptWaveform(indata_bytes):  # 处理音频数据
                result = self.recognizer.Result()
                result_text = json.loads(result)["text"]
                logger.info(f"识别结果：{result_text}")

                # 如果提供了回调函数，立即调用回调函数
                if callback and result_text.strip():
                    callback(result_text)

                if result_text.strip():  # 如果结果不为空，则停止监听
                    raise sd.CallbackStop()
            else:
                partial_result = self.recognizer.PartialResult()
                partial_text = json.loads(partial_result)["partial"]
                logger.debug(f"部分识别：{partial_text}")

                # 如果提供了回调函数，也可以传递部分识别结果
                if callback and partial_text.strip():
                    callback(partial_text, is_final=False)

        try:
            with sd.RawInputStream(samplerate=self.sample_rate, channels=1, dtype='int16', blocksize=4096, callback=audio_callback):
                logger.info(f"开始录音，最大持续时间：{max_duration}毫秒")
                sd.sleep(int(max_duration))  # 最多监听指定时间，可以根据需要调整
        except sd.CallbackStop:
            logger.info("语音识别已完成")
        except Exception as e:
            logger.error(f"语音识别过程中发生错误: {str(e)}")
            raise

        return result_text  # 返回识别结果

    def _callback(self, indata, frames, time, status):
        if status:
            logger.error(f"音频输入错误: {status}")

        # 将 _cffi_backend.buffer 对象转换为 bytes 类型
        indata_bytes = memoryview(indata).tobytes()

        if self.recognizer.AcceptWaveform(indata_bytes):  # 处理音频数据
            result = self.recognizer.Result()
            result_text = json.loads(result)["text"]
            logger.info(f"识别结果：{result_text}")  # 输出文本
        else:
            partial_result = self.recognizer.PartialResult()
            partial_text = json.loads(partial_result)["partial"]
            logger.debug(f"部分识别：{partial_text}")

def recognize_speech_once(model_path=None, sample_rate=8000, max_duration=10000, callback=None):
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
    # 如果未指定模型路径，则使用默认路径
    if model_path is None:
        # 使用兼容打包环境的路径获取方法
        model_path = get_resource_path("Model")

    logger.debug(f"Using model path in recognize_speech_once: {model_path}")

    # 使用单例模式，避免重复初始化模型
    recognizer = VoskRecognizer(model_path, sample_rate)
    return recognizer.recognize_speech(callback=callback, max_duration=max_duration)


if __name__ == "__main__":
    recognizer = VoskRecognizer()
    recognizer.recognize_speech()
