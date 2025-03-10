from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QListWidget, QListWidgetItem, QHBoxLayout, QFrame
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import sqlite3
import os
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
            print(f"数据库查询错误: {str(e)}")
            self.error_occurred.emit(f"数据库查询错误: {str(e)}")


class UserProfileDialog(QDialog):
    def __init__(self, username, parent=None):
        super().__init__(parent)
        self.username = username
        self.setWindowTitle(f"{username}的个人信息")
        self.setMinimumSize(500, 400)

        # 创建主布局
        main_layout = QVBoxLayout(self)

        # 用户信息区域
        info_frame = QFrame()
        info_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        info_layout = QVBoxLayout(info_frame)

        # 用户名标签
        username_label = QLabel(f"用户名: {username}")
        username_label.setStyleSheet('font-size: 18px; font-weight: bold;')
        info_layout.addWidget(username_label)

        # 用户基本信息（可以根据需要扩展）
        info_label = QLabel("个人简介: 模拟面试系统用户")
        info_label.setStyleSheet('font-size: 14px;')
        info_layout.addWidget(info_label)

        # 历史对话区域
        history_label = QLabel("历史面试记录")
        history_label.setStyleSheet('font-size: 16px; font-weight: bold;')

        self.history_list = QListWidget()
        self.history_list.setStyleSheet('font-size: 14px;')

        # 状态标签
        self.status_label = QLabel("正在加载历史记录...")
        self.status_label.setStyleSheet('color: #666; font-size: 14px;')

        # 添加到主布局
        main_layout.addWidget(info_frame)
        main_layout.addWidget(history_label)
        main_layout.addWidget(self.history_list)
        main_layout.addWidget(self.status_label)

        # 启动加载线程
        self.load_thread = UserProfileThread(username)
        self.load_thread.data_ready.connect(self.update_history_list)
        self.load_thread.error_occurred.connect(self.on_error)  # 连接错误信号
        self.load_thread.start()

    def update_history_list(self, history_data):
        """更新历史对话列表"""
        self.history_list.clear()

        if not history_data:
            self.status_label.setText("没有找到历史记录")
            return

        for item in history_data:
            list_item = QListWidgetItem()

            # 创建自定义小部件来显示每条历史记录
            item_widget = QFrame()
            item_layout = QVBoxLayout(item_widget)

            # 对话ID和日期
            id_date_layout = QHBoxLayout()
            id_label = QLabel(f"对话ID: {item[2]}")
            id_label.setStyleSheet('font-weight: bold;')


            id_date_layout.addWidget(id_label)

            id_date_layout.addStretch()

            # 面试模式
            mode_label = QLabel(f"面试模式: {item[1]}")

            item_layout.addLayout(id_date_layout)
            item_layout.addWidget(mode_label)

            # 设置列表项的大小
            list_item.setSizeHint(item_widget.sizeHint())

            # 添加到列表
            self.history_list.addItem(list_item)
            self.history_list.setItemWidget(list_item, item_widget)

        self.status_label.setText(f"共找到 {len(history_data)} 条历史记录")

    def on_error(self, error_msg):
        """处理错误信息"""
        self.status_label.setText(f"错误: {error_msg}")
        self.history_list.clear()