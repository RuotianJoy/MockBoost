from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt6.QtCore import Qt, pyqtSignal
from db.controller.UserServerController import UserServerController

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('MockBoost 登录')
        self.setFixedSize(400, 300)
        self.setup_ui()
        
    def setup_ui(self):
        # 创建主布局
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # 添加标题
        title = QLabel('MockBoost 模拟面试系统')
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet('font-size: 20px; font-weight: bold; margin-bottom: 20px;')
        layout.addWidget(title)
        
        # 用户名输入框
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText('请输入用户名')
        self.username_input.setStyleSheet('padding: 8px; border: 1px solid #ccc; border-radius: 4px;')
        layout.addWidget(self.username_input)

        
        # 密码输入框
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText('请输入密码')
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setStyleSheet('padding: 8px; border: 1px solid #ccc; border-radius: 4px;')
        layout.addWidget(self.password_input)

        
        # 登录按钮
        login_button = QPushButton('登录')
        login_button.setStyleSheet(
            'QPushButton {'
            '   background-color: #4CAF50;'
            '   color: white;'
            '   padding: 10px;'
            '   border: none;'
            '   border-radius: 4px;'
            '   font-size: 16px;'
            '}'
            'QPushButton:hover {'
            '   background-color: #45a049;'
            '}'
        )
        login_button.clicked.connect(self.handle_login)
        layout.addWidget(login_button)
        
        # 设置窗口布局
        self.setLayout(layout)
        
    def handle_login(self):
        # 这里应该添加实际的用户验证逻辑
        username = self.username_input.text()
        password = self.password_input.text()
        print(username, password)

        if username and password:  # 简单的非空验证

            data = {
                'username': username,
                'password': password,
            }
            con = UserServerController()
            res = con.findlogin_user_ServerStatus(data)
            print(res)
            if res:
                self.open_main_window()
        else:
            QMessageBox.warning(self, '登录失败', '请输入用户名和密码')
    
    def open_main_window(self):
        # 这个方法将被AppController覆盖
        pass