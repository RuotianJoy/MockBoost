from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QListWidget, QListWidgetItem, QHBoxLayout, QFrame, QTextEdit, \
    QSplitter
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import sqlite3
import os
import json
import redis
from db.controller.UserServerController import UserServerController


class UserProfileThread(QThread):
    """用户信息加载线程"""
    data_ready = pyqtSignal(list)  # 数据准备好的信号
    error_occurred = pyqtSignal(str)  # 添加错误信号

    def __init__(self, username):
        super().__init__()
        self.username = username

    def run(self):
        try:
            # 从数据库加载历史对话ID
            con = UserServerController()
            userinfo = {
                'username': self.username,
            }
            uid = con.getUid(userinfo)
            print(uid)

            userdata = {
                "Uid": uid[0][6]
            }

            res = con.find_dialog_info(userdata)

            # 发送数据准备好的信号
            self.data_ready.emit(res if res else [])

        except Exception as e:
            print(f"DB Error: {str(e)}")
            self.error_occurred.emit(f"Error in DB: {str(e)}")


class ChatHistoryThread(QThread):
    """聊天历史加载线程"""
    data_ready = pyqtSignal(str)  # 数据准备好的信号
    error_occurred = pyqtSignal(str)  # 错误信号

    def __init__(self, dialog_id):
        super().__init__()
        self.dialog_id = dialog_id

        # Redis连接配置（需要替换为实际的阿里云Redis连接信息）
        self.redis_host = "r-bp162llfgqnxpesejnpd.redis.rds.aliyuncs.com"
        self.redis_port = 6379
        self.redis_password = "Liao031221"


    def run(self):
        try:
            # 连接Redis
            r = redis.Redis(
                host=self.redis_host,
                port=self.redis_port,
                password=self.redis_password,
                decode_responses=True  # 自动将响应解码为字符串
            )

            # 使用对话ID作为键获取对话历史
            chat_history = r.get(self.dialog_id)

            if chat_history:
                self.data_ready.emit(chat_history)
            else:
                self.error_occurred.emit(f"Can find the ID: {self.dialog_id} history record'")

        except Exception as e:
            print(f"Redis查询错误: {str(e)}")
            self.error_occurred.emit(f"Redis查询错误: {str(e)}")


class ChatHistoryDialog(QDialog):
    """聊天历史对话框"""

    def __init__(self, dialog_id, interview_mode, parent=None):
        super().__init__(parent)
        self.dialog_id = dialog_id
        self.setWindowTitle(f"Interview history - ID: {dialog_id}")
        self.setMinimumSize(600, 500)

        # 创建布局
        layout = QVBoxLayout(self)

        # 添加基本信息
        info_frame = QFrame()
        info_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        info_layout = QVBoxLayout(info_frame)

        id_label = QLabel(f"Interview ID: {dialog_id}")
        id_label.setStyleSheet('font-weight: bold; font-size: 16px;')
        info_layout.addWidget(id_label)

        mode_label = QLabel(f"Desired position: {interview_mode}")
        mode_label.setStyleSheet('font-size: 14px;')
        info_layout.addWidget(mode_label)

        layout.addWidget(info_frame)

        # 添加对话内容显示区域
        self.chat_content = QTextEdit()
        self.chat_content.setReadOnly(True)
        self.chat_content.setStyleSheet('font-size: 14px; line-height: 1.5;')
        layout.addWidget(self.chat_content)

        # 状态标签
        self.status_label = QLabel("Loading History...")
        self.status_label.setStyleSheet('color: #666; font-size: 14px;')
        layout.addWidget(self.status_label)

        # 启动加载线程
        self.load_thread = ChatHistoryThread(dialog_id)
        self.load_thread.data_ready.connect(self.display_chat_history)
        self.load_thread.error_occurred.connect(self.on_error)
        self.load_thread.start()

    def display_chat_history(self, chat_history):
        """显示聊天历史"""
        try:
            # 尝试解析JSON
            chat_data = json.loads(chat_history)

            # 格式化显示
            formatted_chat = ""

            for message in chat_data:
                if isinstance(message, dict):
                    # 根据实际的数据结构进行调整
                    role = message.get('role', '未知')
                    content = message.get('content', '')

                    if role.lower() == 'user':
                        formatted_chat += f"<p><b style='color: #0066cc;'>You:</b> {content}</p>"
                    elif role.lower() == 'assistant':
                        formatted_chat += f"<p><b style='color: #009933;'>Interviewer:</b> {content}</p>"
                    else:
                        formatted_chat += f"<p><b>{role}:</b> {content}</p>"

                    formatted_chat += "<hr>"
                elif isinstance(message, str):
                    formatted_chat += f"<p>{message}</p><hr>"

            self.chat_content.setHtml(formatted_chat)
            self.status_label.setText("History Loaded")

        except json.JSONDecodeError:
            # 如果不是JSON格式，直接显示文本
            self.chat_content.setPlainText(chat_history)
            self.status_label.setText("History Loaded(orignal)")

    def on_error(self, error_msg):
        """处理错误信息"""
        self.status_label.setText(f"error: {error_msg}")
        self.chat_content.setPlainText(f"Error in Loading History: {error_msg}")


class UserProfileDialog(QDialog):
    def __init__(self, username, parent=None):
        super().__init__(parent)
        self.username = username
        self.setWindowTitle(f"{username}'s Profile")
        self.setMinimumSize(500, 400)

        # 创建主布局
        main_layout = QVBoxLayout(self)

        # 用户信息区域
        info_frame = QFrame()
        info_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        info_layout = QVBoxLayout(info_frame)

        # 用户名标签
        username_label = QLabel(f"Username: {username}")
        username_label.setStyleSheet('font-size: 18px; font-weight: bold;')
        info_layout.addWidget(username_label)

        # 用户基本信息（可以根据需要扩展）
        info_label = QLabel("Identity: Mock interview system user")
        info_label.setStyleSheet('font-size: 14px;')
        info_layout.addWidget(info_label)

        # 历史对话区域
        history_label = QLabel("Interview History")
        history_label.setStyleSheet('font-size: 16px; font-weight: bold;')

        self.history_list = QListWidget()
        self.history_list.setStyleSheet('font-size: 14px;')
        # 连接双击事件
        self.history_list.itemDoubleClicked.connect(self.open_chat_history)

        # 状态标签
        self.status_label = QLabel("Loading History...")
        self.status_label.setStyleSheet('color: #666; font-size: 14px;')

        # 添加到主布局
        main_layout.addWidget(info_frame)
        main_layout.addWidget(history_label)
        main_layout.addWidget(self.history_list)
        main_layout.addWidget(self.status_label)

        # 存储对话数据
        self.history_data = []

        # 启动加载线程
        self.load_thread = UserProfileThread(username)
        self.load_thread.data_ready.connect(self.update_history_list)
        self.load_thread.error_occurred.connect(self.on_error)  # 连接错误信号
        self.load_thread.start()

    def update_history_list(self, history_data):
        """更新历史对话列表"""
        self.history_list.clear()
        self.history_data = history_data  # 保存数据以便后续使用

        if not history_data:
            self.status_label.setText("No history")
            return

        for item in history_data:
            list_item = QListWidgetItem()

            # 创建自定义小部件来显示每条历史记录
            item_widget = QFrame()
            item_layout = QVBoxLayout(item_widget)

            # 对话ID和日期
            id_date_layout = QHBoxLayout()
            dialog_id = item[2]
            id_label = QLabel(f"Dialog ID: {dialog_id}")
            id_label.setStyleSheet('font-weight: bold;')

            id_date_layout.addWidget(id_label)
            id_date_layout.addStretch()

            # 面试模式
            interview_mode = item[1]
            mode_label = QLabel(f"Intended position: {interview_mode}")

            # 双击提示
            hint_label = QLabel("Double-click to view the detailed conversation")
            hint_label.setStyleSheet('color: #666; font-style: italic;')

            item_layout.addLayout(id_date_layout)
            item_layout.addWidget(mode_label)
            item_layout.addWidget(hint_label)

            # 设置列表项的大小
            list_item.setSizeHint(item_widget.sizeHint())

            # 保存对话ID和面试模式，用于后续打开详情
            list_item.setData(Qt.ItemDataRole.UserRole, {'dialog_id': dialog_id, 'interview_mode': interview_mode})

            # 添加到列表
            self.history_list.addItem(list_item)
            self.history_list.setItemWidget(list_item, item_widget)

        self.status_label.setText(f"Found {len(history_data)} history record. Double-click to view the detailed conversation.")

    def on_error(self, error_msg):
        """处理错误信息"""
        self.status_label.setText(f"错误: {error_msg}")
        self.history_list.clear()

    def open_chat_history(self, item):
        """打开聊天历史对话框"""
        item_data = item.data(Qt.ItemDataRole.UserRole)
        dialog_id = item_data['dialog_id']
        interview_mode = item_data['interview_mode']

        # 创建并显示对话历史对话框
        dialog = ChatHistoryDialog(dialog_id, interview_mode, self)
        dialog.exec()