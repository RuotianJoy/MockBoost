import os

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, \
    QTextEdit, QFrame, QComboBox, QLineEdit
from PyQt6.QtCore import QThread, pyqtSignal
import sys
from TTSandASR.ChatTTs import ChatTTS
from TTSandASR.Vosk import recognize_speech_once, get_resource_path
from Main.Thread.ModelThread import ModelThread
from Main.Thread.EndInterviewThread import EndInterviewThread
from user_profile import UserProfileDialog


class TTSThread(QThread):
    """TTS语音合成线程"""
    finished = pyqtSignal()  # 完成信号

    def __init__(self, text):
        super().__init__()
        self.text = text
        self.tts = ChatTTS()

    def run(self):
        # 在线程中执行TTS语音合成和播放
        self.tts.play_text(self.text)
        self.finished.emit()  # 发送完成信号


class ASRThread(QThread):
    """语音识别线程"""
    result_ready = pyqtSignal(str)  # 识别结果信号
    partial_result_ready = pyqtSignal(str)  # 部分识别结果信号

    def __init__(self, model_path=None, sample_rate=8000, max_duration=50000):
        super().__init__()
        # 使用get_resource_path获取兼容打包环境的模型路径
        self.model_path = model_path if model_path else get_resource_path("Model")
        print("ASRThread model_path: " + str(self.model_path))
        self.sample_rate = sample_rate
        self.max_duration = max_duration
        
    def run(self):
        # 在线程中执行语音识别，添加回调函数实现实时反馈
        def result_callback(text, is_final=True):
            if is_final:
                self.result_ready.emit(text)  # 发送最终识别结果信号
            else:
                self.partial_result_ready.emit(text)  # 发送部分识别结果信号
                
        # 使用回调函数执行语音识别
        recognize_speech_once(self.model_path, self.sample_rate, self.max_duration, callback=result_callback)


class MainWindow(QMainWindow):
    def __init__(self, username):
        super().__init__()
        self.setWindowTitle('MockBoost')
        self.setMinimumSize(1000, 700)
        self.username = username
        self.conversation_id = None  # 添加conversation_id属性用于保存对话ID
        # 创建主窗口部件
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # 创建主布局
        main_layout = QHBoxLayout(main_widget)

        # 左侧控制面板
        left_panel = QFrame()
        left_panel.setFrameStyle(QFrame.Shape.StyledPanel)
        left_layout = QVBoxLayout(left_panel)

        # 面试模式选择
        mode_label = QLabel('Intended position')
        mode_label.setStyleSheet('font-size: 16px; font-weight: bold;')

        self.mode_combo = QComboBox()
        self.mode_combo.addItems(['Java developer', 'Python developer', 'Front-end developer', 'Algorithm Engineer'])
        self.mode_combo.setEditable(True)  # 允许用户自定义输入
        self.mode_combo.setStyleSheet('padding: 5px; font-size: 14px;')

        # 开始面试按钮
        start_button = QPushButton('Start interview')
        start_button.setStyleSheet(
            'QPushButton {'
            '    background-color: #4CAF50;'
            '    color: white;'
            '    padding: 10px;'
            '    border: none;'
            '    border-radius: 4px;'
            '    font-size: 14px;'
            '}'
            'QPushButton:hover {'
            '    background-color: #45a049;'
            '}'
        )

        # 结束面试按钮
        end_button = QPushButton('End interview')
        end_button.setStyleSheet(
            'QPushButton {'
            '    background-color: #f44336;'
            '    color: white;'
            '    padding: 10px;'
            '    border: none;'
            '    border-radius: 4px;'
            '    font-size: 14px;'
            '}'
            'QPushButton:hover {'
            '    background-color: #da190b;'
            '}'
        )

        # 添加到左侧布局
        left_layout.addWidget(mode_label)
        left_layout.addWidget(self.mode_combo)
        left_layout.addWidget(start_button)
        left_layout.addWidget(end_button)
        left_layout.addStretch()
        
        # 用户图标按钮
        user_button = QPushButton('👤 Personal INFO')
        user_button.setStyleSheet(
            'QPushButton {'
            '    background-color: #2196F3;'
            '    color: white;'
            '    padding: 10px;'
            '    border: none;'
            '    border-radius: 4px;'
            '    font-size: 14px;'
            '}'
            'QPushButton:hover {'
            '    background-color: #0b7dda;'
            '}'
        )
        left_layout.addWidget(user_button)

        # 右侧对话区域
        right_panel = QFrame()
        right_panel.setFrameStyle(QFrame.Shape.StyledPanel)
        right_layout = QVBoxLayout(right_panel)

        # 对话历史显示区
        chat_label = QLabel('Conversation')
        chat_label.setStyleSheet('font-size: 16px; font-weight: bold;')
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        self.chat_history.setStyleSheet('font-size: 14px;')

        # 语音状态显示
        self.status_label = QLabel('Initialization...')
        self.status_label.setStyleSheet('color: #666; font-size: 14px;')

        # 输入框和语音按钮的水平布局
        input_layout = QHBoxLayout()
        
        # 输入框
        self.input_field = QLineEdit(self)  # 新增输入框
        self.input_field.setPlaceholderText("Please enter your response...")
        self.input_field.setStyleSheet('padding: 10px; font-size: 14px;')
        
        # 语音识别按钮
        self.voice_button = QPushButton('🎤')
        self.voice_button.setToolTip('语音输入')
        self.voice_button.setStyleSheet(
            'QPushButton {'
            '    background-color: #FF9800;'
            '    color: white;'
            '    padding: 10px;'
            '    border: none;'
            '    border-radius: 4px;'
            '    font-size: 14px;'
            '    min-width: 40px;'
            '}'
            'QPushButton:hover {'
            '    background-color: #F57C00;'
            '}'
        )
        
        # 添加到输入布局
        input_layout.addWidget(self.input_field, 9)  # 输入框占据大部分空间
        input_layout.addWidget(self.voice_button, 1)  # 语音按钮占据较小空间

        # 添加到右侧布局
        right_layout.addWidget(chat_label)
        right_layout.addWidget(self.chat_history)
        right_layout.addWidget(self.status_label)
        right_layout.addLayout(input_layout)  # 添加输入布局

        # 添加到主布局
        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(right_panel, 4)

        # 连接信号
        start_button.clicked.connect(self.start_interview)
        end_button.clicked.connect(self.end_interview)
        self.input_field.returnPressed.connect(self.handle_input)  # 监听回车按键事件
        user_button.clicked.connect(self.show_user_profile)  # 连接用户图标按钮点击事件
        self.voice_button.clicked.connect(self.start_voice_recognition)  # 连接语音识别按钮点击事件

    def start_interview(self):
        """开始模拟面试"""
        mode = self.mode_combo.currentText()

        self.chat_history.append(f'Welcome, {self.username}! Conducting a {mode} mock interview...\n')
        self.status_label.setText('System: Interview is being initialized...')
        
        # 创建并启动模型交互线程
        initial_prompt = f"Hello, I'm {self.username} and I'm looking to interview for a career in {mode}"
        self.model_thread = ModelThread(initial_prompt, None, self.username, mode)
        self.model_thread.response_ready.connect(self.on_interview_start)
        self.model_thread.error_occurred.connect(self.on_model_error)  # 连接错误信号
        self.model_thread.start()
        
    def handle_input(self):
        """处理用户输入并获取回应"""
        user_input = self.input_field.text()
        if user_input:
            # 立即显示用户输入到界面上
            self.chat_history.append(f"\n{self.username}: {user_input}\n")
            self.input_field.clear()

            # 更新状态提示用户系统正在处理
            self.status_label.setText('System: Thinking...')

            # 确保UI更新
            QApplication.processEvents()
            
            # 检查并等待之前的模型线程完成
            if hasattr(self, 'model_thread') and self.model_thread.isRunning():
                try:
                    # 尝试断开之前的信号连接
                    self.model_thread.response_ready.disconnect()
                    self.model_thread.error_occurred.disconnect()  # 断开错误信号连接
                except TypeError:
                    # 如果信号未连接，会抛出TypeError
                    pass
                # 等待线程完成
                self.model_thread.wait()

            # 创建并启动新的模型交互线程
            self.model_thread = ModelThread(user_input, self.conversation_id, self.username)
            self.model_thread.response_ready.connect(self.on_model_response)
            self.model_thread.error_occurred.connect(self.on_model_error)  # 连接错误信号
            self.model_thread.start()
            
    def on_interview_start(self, response, conversation_id):
        """面试开始后的回调"""
        # 更新对话ID
        self.conversation_id = conversation_id
        self.chat_history.append(f"\nInterviewer: {response}\n")
        self.status_label.setText(f'\nSystem: Start Mock Interview, Conversation ID：{self.conversation_id}\n')
        
        # 检查并停止之前的TTS线程
        if hasattr(self, 'tts_thread') and self.tts_thread.isRunning():
            # 断开之前的TTS线程信号连接
            try:
                self.tts_thread.finished.disconnect()
            except TypeError:
                # 如果信号未连接，会抛出TypeError
                pass
            self.tts_thread.wait()
        
        # 创建并启动TTS线程
        self.tts_thread = TTSThread(response)
        self.tts_thread.finished.connect(self.on_tts_finished)
        self.tts_thread.start()
        
        self.status_label.setText(f'System: Voice playback...')
        
        # 安全地断开信号连接，避免多次连接同一信号
        try:
            if hasattr(self, 'model_thread'):
                self.model_thread.response_ready.disconnect(self.on_interview_start)
        except TypeError:
            # 如果信号未连接，会抛出TypeError
            pass
            
        # 等待线程完成
        if hasattr(self, 'model_thread') and self.model_thread.isRunning():
            self.model_thread.wait()

    def end_interview(self):
        """结束模拟面试"""
        # 检查并停止模型线程
        if hasattr(self, 'model_thread') and self.model_thread.isRunning():
            try:
                # 尝试断开模型线程的信号连接
                self.model_thread.response_ready.disconnect()
                self.model_thread.error_occurred.disconnect()
            except TypeError:
                # 如果信号未连接，会抛出TypeError
                pass
            # 等待线程完成
            self.model_thread.wait()
        
        # 检查并停止TTS线程
        if hasattr(self, 'tts_thread') and self.tts_thread.isRunning():
            try:
                # 断开TTS线程信号连接
                self.tts_thread.finished.disconnect()
            except TypeError:
                # 如果信号未连接，会抛出TypeError
                pass
            # 等待线程完成
            self.tts_thread.wait()
        
        # 更新UI状态
        self.status_label.setText('Interviews are being concluded...')
        self.chat_history.append('\nSystem: Interview is ending, please wait...\n')
        
        # 确保UI更新
        QApplication.processEvents()
        
        # 创建并启动结束面试线程
        if self.conversation_id:
            self.end_thread = EndInterviewThread(self.conversation_id, self.username, self.mode_combo.currentText())
            self.end_thread.finished.connect(self.on_end_interview_finished)
            self.end_thread.error_occurred.connect(self.on_end_interview_error)
            self.end_thread.start()
        else:
            # 如果没有对话ID，直接完成结束面试
            self.on_end_interview_finished(True, "The interview is over")

    def on_end_interview_finished(self, success, message):
        """结束面试线程完成后的回调"""
        # 重置对话状态
        self.conversation_id = None
        
        # 更新UI状态
        self.status_label.setText(message)
        self.chat_history.append(f'\nSystem: {message}\n')
        self.chat_history.clear()
        # 清空输入框
        self.input_field.clear()
        
        # 确保UI更新
        QApplication.processEvents()
        
        # 安全地断开结束面试线程的信号连接
        if hasattr(self, 'end_thread'):
            try:
                self.end_thread.finished.disconnect()
                self.end_thread.error_occurred.disconnect()
            except TypeError:
                # 如果信号未连接，会抛出TypeError
                pass
    
    def on_end_interview_error(self, error_msg):
        """处理结束面试线程错误"""
        # 在界面上显示错误信息
        self.chat_history.append(f'\nSystem Error: {error_msg}\n')
        self.status_label.setText('System: An error occurred at the end of the interview')
        
        # 确保UI更新
        QApplication.processEvents()

    def on_model_response(self, response, conversation_id):
        """模型回应准备好后的回调"""
        # 更新对话ID
        self.conversation_id = conversation_id
        
        # 检查并停止之前的TTS线程
        if hasattr(self, 'tts_thread') and self.tts_thread.isRunning():
            # 断开之前的TTS线程信号连接
            try:
                self.tts_thread.finished.disconnect()
            except TypeError:
                # 如果信号未连接，会抛出TypeError
                pass
            self.tts_thread.wait()
        
        # 直接显示完整的系统回应
        self.chat_history.append(f'\nInterviewer:  {response}\n')
        
        # 创建并启动TTS线程
        self.tts_thread = TTSThread(response)
        self.tts_thread.finished.connect(self.on_tts_finished)
        self.tts_thread.start()
        
        self.status_label.setText(f'System: Voice playback...')
        
        # 安全地断开模型线程的信号连接
        try:
            if hasattr(self, 'model_thread'):
                self.model_thread.response_ready.disconnect(self.on_model_response)
        except TypeError:
            # 如果信号未连接，会抛出TypeError
            pass
            
        # 等待模型线程完成
        if hasattr(self, 'model_thread') and self.model_thread.isRunning():
            self.model_thread.wait()
            
    def on_tts_finished(self):
        """TTS播放完成后的回调"""
        self.status_label.setText(f'System: The ID of the current conversation：{self.conversation_id}')
        
        # 安全地断开TTS线程的信号连接
        try:
            if hasattr(self, 'tts_thread'):
                self.tts_thread.finished.disconnect(self.on_tts_finished)
        except TypeError:
            # 如果信号未连接，会抛出TypeError
            pass
            
        # 等待TTS线程完成
        if hasattr(self, 'tts_thread') and self.tts_thread.isRunning():
            self.tts_thread.wait()
    
    def on_model_error(self, error_msg):
        """处理模型线程错误"""
        # 在界面上显示错误信息
        self.chat_history.append(f'\nSystem Error: {error_msg}\n')
        self.status_label.setText('System: An error has occurred, please try again')
        
        # 确保UI更新
        QApplication.processEvents()

    def show_user_profile(self):
        """显示用户个人信息页面"""
        # 创建并显示用户信息对话框
        profile_dialog = UserProfileDialog(self.username, self)
        profile_dialog.exec()
        
    def start_voice_recognition(self):
        """启动语音识别"""
        # 更新状态提示用户系统正在进行语音识别
        self.status_label.setText('System: 正在进行语音识别，请说话...')
        self.voice_button.setEnabled(False)  # 禁用语音按钮，防止重复点击
        
        # 确保UI更新
        QApplication.processEvents()
        
        # 检查并等待之前的语音识别线程完成
        if hasattr(self, 'asr_thread') and self.asr_thread.isRunning():
            try:
                # 尝试断开之前的信号连接
                self.asr_thread.result_ready.disconnect()
                self.asr_thread.partial_result_ready.disconnect()
            except TypeError:
                # 如果信号未连接，会抛出TypeError
                pass
            # 等待线程完成
            self.asr_thread.wait()
        
        # 创建并启动新的语音识别线程
        self.asr_thread = ASRThread()
        self.asr_thread.result_ready.connect(self.on_speech_recognized)
        self.asr_thread.partial_result_ready.connect(self.on_partial_speech_recognized)
        self.asr_thread.start()
    
    def on_speech_recognized(self, result):
        """语音识别完成后的回调"""
        # 将识别结果填入输入框
        self.input_field.setText(result)
        self.status_label.setText('System: 语音识别完成')
        self.voice_button.setEnabled(True)  # 重新启用语音按钮
        
        # 确保UI更新
        QApplication.processEvents()
    
    def on_partial_speech_recognized(self, partial_result):
        """部分语音识别结果的回调"""
        # 将部分识别结果实时显示在输入框中
        self.input_field.setText(partial_result)
        
        # 确保UI更新
        QApplication.processEvents()

def main():
    app = QApplication(sys.argv)
    window = MainWindow('user1')  # 传入用户名
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
