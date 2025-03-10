from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, \
    QTextEdit, QFrame, QComboBox, QLineEdit
from PyQt6.QtCore import Qt
import sys
from TTSandASR.ChatTTs import ChatTTS

from wandb import login
from Main.DeepSeek import start_interview_ds


class MainWindow(QMainWindow):
    def __init__(self, username):
        super().__init__()
        self.setWindowTitle('MockBoost 模拟面试系统')
        self.setMinimumSize(1000, 700)
        self.username = username
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
        mode_label = QLabel('面试模式')
        mode_label.setStyleSheet('font-size: 16px; font-weight: bold;')

        self.mode_combo = QComboBox()
        self.mode_combo.addItems(['Java开发', 'Python开发', '前端开发', '算法工程师'])
        self.mode_combo.setEditable(True)  # 允许用户自定义输入
        self.mode_combo.setStyleSheet('padding: 5px; font-size: 14px;')

        # 开始面试按钮
        start_button = QPushButton('开始面试')
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
        end_button = QPushButton('结束面试')
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

        # 右侧对话区域
        right_panel = QFrame()
        right_panel.setFrameStyle(QFrame.Shape.StyledPanel)
        right_layout = QVBoxLayout(right_panel)

        # 对话历史显示区
        chat_label = QLabel('对话历史')
        chat_label.setStyleSheet('font-size: 16px; font-weight: bold;')
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        self.chat_history.setStyleSheet('font-size: 14px;')

        # 语音状态显示
        self.status_label = QLabel('准备就绪')
        self.status_label.setStyleSheet('color: #666; font-size: 14px;')

        # 输入框
        self.input_field = QLineEdit(self)  # 新增输入框
        self.input_field.setPlaceholderText("请输入您的回答...")
        self.input_field.setStyleSheet('padding: 10px; font-size: 14px;')

        # 添加到右侧布局
        right_layout.addWidget(chat_label)
        right_layout.addWidget(self.chat_history)
        right_layout.addWidget(self.status_label)
        right_layout.addWidget(self.input_field)  # 添加输入框

        # 添加到主布局
        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(right_panel, 4)

        # 连接信号
        start_button.clicked.connect(self.start_interview)
        end_button.clicked.connect(self.end_interview)

    def start_interview(self):
        """开始模拟面试"""
        mode = self.mode_combo.currentText()

        self.chat_history.append(f'欢迎您，{self.username} 正在进行{mode}模拟面试...\n')

        # TODO: 在这里添加实际的面试逻辑
        response, chatid = start_interview_ds(
            f"Hello, I'm {self.username} and I'm looking to interview for a career in {mode}")
        self.chat_history.append(f'SYS:  {response}')
        tts = ChatTTS()
        tts.play_text(response)
        self.status_label.setText(f'\n系统: 开始{mode}模拟面试, 对话ID：{chatid}\n')

    def end_interview(self):
        """结束模拟面试"""
        self.status_label.setText('面试已结束')
        self.chat_history.append('\n系统: 面试结束\n')
        # TODO: 在这里添加面试结束的处理逻辑


def main():
    app = QApplication(sys.argv)
    window = MainWindow('用户1')  # 传入用户名
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
