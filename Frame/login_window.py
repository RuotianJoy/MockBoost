from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal
from db.controller.UserServerController import UserServerController
from Frame.register_window import RegisterWindow

class LoginWindow(QWidget):
    switch_to_register = pyqtSignal()  # 切换到注册窗口信号
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle('MockBoost 登录')
        self.setFixedSize(400, 350)
        self.register_window = None
        self.setup_ui()
        
    def setup_ui(self):
        # 创建主布局
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # 添加标题
        title = QLabel('MockBoost')
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet('font-size: 20px; font-weight: bold; margin-bottom: 20px;')
        layout.addWidget(title)
        
        # 用户名输入框
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText('Please enter a username')
        self.username_input.setStyleSheet('padding: 8px; border: 1px solid #ccc; border-radius: 4px;')
        layout.addWidget(self.username_input)

        
        # 密码输入框
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText('Please enter your password')
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setStyleSheet('padding: 8px; border: 1px solid #ccc; border-radius: 4px;')
        layout.addWidget(self.password_input)

        
        # 按钮布局
        button_layout = QHBoxLayout()
        
        # 登录按钮
        login_button = QPushButton('Login')
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
        
        # 注册按钮
        register_button = QPushButton('Register')
        register_button.setStyleSheet(
            'QPushButton {'
            '   background-color: #2196F3;'
            '   color: white;'
            '   padding: 10px;'
            '   border: none;'
            '   border-radius: 4px;'
            '   font-size: 16px;'
            '}'
            'QPushButton:hover {'
            '   background-color: #0b7dda;'
            '}'
        )
        register_button.clicked.connect(self.show_register_window)
        
        button_layout.addWidget(login_button)
        button_layout.addWidget(register_button)
        layout.addLayout(button_layout)
        
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
        
    def show_register_window(self):
        # 显示注册窗口
        if not self.register_window:
            self.register_window = RegisterWindow()
            self.register_window.switch_to_login.connect(self.show_from_register)
            self.register_window.register_success.connect(self.set_username_from_register)
        self.register_window.show()
        self.hide()
    
    def show_from_register(self):
        # 从注册窗口返回登录窗口
        if self.register_window:
            self.register_window.hide()
        self.show()
    
    def set_username_from_register(self, username):
        # 设置从注册窗口获取的用户名
        self.username_input.setText(username)