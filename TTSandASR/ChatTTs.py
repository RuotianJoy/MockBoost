from TTS.api import TTS
import sounddevice as sd
import numpy as np

class ChatTTS:
    def __init__(self, model_name="tts_models/en/ljspeech/glow-tts", sample_rate=22050):
        # 加载预训练的 TTS 模型
        self.model = TTS(model_name=model_name)
        self.sample_rate = sample_rate

    def play_text(self, text):
        # 将文本转化为语音数据
        audio_array = self.model.tts(text)
        
        # 通过 sounddevice 播放音频
        sd.play(audio_array, self.sample_rate)
        sd.wait()  # 等待播放完毕

        print("Audio played.")

# Example usage:
# tts = ChatTTS()
# tts.play_text("Hello, this is a test of the Coqui TTS system. I hope you're feeling happy today!")

