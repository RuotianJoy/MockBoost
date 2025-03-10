from PyQt6.QtCore import QThread, pyqtSignal
from Main.Thread.DataThread import DataThread

class ModelThread(QThread):
    """模型交互线程，用于调用大模型获取回答"""
    response_ready = pyqtSignal(str, str)  # 回答准备好信号，传递回答内容和对话ID
    error_occurred = pyqtSignal(str)  # 错误信号，传递错误信息
    
    def __init__(self, user_input, conversation_id=None, username=None, mode = None):
        super().__init__()
        self.user_input = user_input
        self.username = username
        self.conversation_id = conversation_id
        self.mode = mode
        
    def run(self):
        # 创建数据获取线程
        self.data_thread = DataThread(self.user_input, self.conversation_id, self.username, self.mode)
        
        # 连接信号
        self.data_thread.data_ready.connect(self.on_data_ready)
        self.data_thread.error_occurred.connect(self.on_error)
        
        # 启动数据获取线程
        self.data_thread.start()
        
    def on_data_ready(self, response, conversation_id):
        # 数据准备好后，发送回答准备好的信号
        self.response_ready.emit(response, conversation_id)
        
    def on_error(self, error_msg):
        # 发生错误时，发送错误信号
        self.error_occurred.emit(error_msg)
        print(f"ModelThread 捕获到错误: {error_msg}")