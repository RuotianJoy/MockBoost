from PyQt6.QtCore import QThread, pyqtSignal
import time

class TextDisplayThread(QThread):
    """文本显示线程，用于逐字显示文本"""
    update_text = pyqtSignal(str)  # 更新文本信号
    finished = pyqtSignal()  # 完成信号
    
    def __init__(self, text, speed=0.05):
        super().__init__()
        self.text = text
        self.speed = speed  # 显示速度，每个字符之间的间隔时间（秒）
        self.is_running = True
        
    def run(self):
        # 逐字显示文本
        displayed_text = ""
        for char in self.text:
            if not self.is_running:
                break
            displayed_text += char
            self.update_text.emit(displayed_text)
            time.sleep(self.speed)
        
        self.finished.emit()  # 发送完成信号
    
    def stop(self):
        """停止线程"""
        self.is_running = False