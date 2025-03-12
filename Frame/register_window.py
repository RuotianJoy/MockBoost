import random

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal
from db.controller.UserServerController import UserServerController
from Email.get_email_api import send_email

class RegisterWindow(QWidget):
    register_success = pyqtSignal(str)  # 注册成功信号，传递用户名
    switch_to_login = pyqtSignal()  # 切换到登录窗口信号
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle('MockBoost 注册')
        self.setFixedSize(400, 500)  # 增加窗口高度以容纳验证码输入框
        self.verification_code = None  # 存储验证码
        self.email_verified = False  # 邮箱验证状态
        self.setup_ui()
        
    def setup_ui(self):
        # 创建主布局
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # 添加标题
        title = QLabel('注册新账户')
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
        
        # 确认密码输入框
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText('请确认密码')
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_input.setStyleSheet('padding: 8px; border: 1px solid #ccc; border-radius: 4px;')
        layout.addWidget(self.confirm_password_input)
        
        # 手机号输入框
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText('请输入手机号')
        self.phone_input.setStyleSheet('padding: 8px; border: 1px solid #ccc; border-radius: 4px;')
        layout.addWidget(self.phone_input)
        
        # 邮箱输入框和验证按钮的水平布局
        email_layout = QHBoxLayout()
        
        # 邮箱输入框
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText('请输入邮箱')
        self.email_input.setStyleSheet('padding: 8px; border: 1px solid #ccc; border-radius: 4px;')
        email_layout.addWidget(self.email_input)
        
        # 验证按钮
        self.verify_button = QPushButton('发送验证码')
        self.verify_button.setStyleSheet(
            'QPushButton {'
            '   background-color: #FF9800;'
            '   color: white;'
            '   padding: 8px;'
            '   border: none;'
            '   border-radius: 4px;'
            '   font-size: 14px;'
            '}'
            'QPushButton:hover {'
            '   background-color: #F57C00;'
            '}'
        )
        self.verify_button.clicked.connect(self.send_verification_code)
        email_layout.addWidget(self.verify_button)
        
        layout.addLayout(email_layout)
        
        # 验证码输入框
        self.verification_input = QLineEdit()
        self.verification_input.setPlaceholderText('请输入验证码')
        self.verification_input.setStyleSheet('padding: 8px; border: 1px solid #ccc; border-radius: 4px;')
        layout.addWidget(self.verification_input)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        
        # 注册按钮
        register_button = QPushButton('注册')
        register_button.setStyleSheet(
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
        register_button.clicked.connect(self.handle_register)
        
        # 返回登录按钮
        back_button = QPushButton('返回登录')
        back_button.setStyleSheet(
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
        back_button.clicked.connect(self.switch_to_login.emit)
        
        button_layout.addWidget(register_button)
        button_layout.addWidget(back_button)
        layout.addLayout(button_layout)
        
        # 设置窗口布局
        self.setLayout(layout)
    
    def send_verification_code(self):
        # 获取邮箱地址
        email = self.email_input.text()
        if not email:
            QMessageBox.warning(self, '验证失败', '请输入邮箱地址')
            return
        
        try:
            # 发送验证码邮件
            self.verification_code = send_email(email)
            QMessageBox.information(self, '验证码已发送', f'验证码已发送到邮箱 {email}，请查收')
            self.verify_button.setEnabled(False)  # 禁用按钮防止重复发送
            self.verify_button.setText('已发送')  # 更新按钮文本
        except Exception as e:
            QMessageBox.warning(self, '发送失败', f'验证码发送失败: {str(e)}')
    
    def handle_register(self):
        # 获取输入信息
        username = self.username_input.text()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()
        userid = 'U' + str(random.randint(100001, 999999))
        phone = self.phone_input.text()
        email = self.email_input.text()
        verification_input = self.verification_input.text()
        
        # 验证输入
        if not (username and password and confirm_password and userid and phone and email and verification_input):
            QMessageBox.warning(self, '注册失败', '请填写所有字段')
            return
        
        if password != confirm_password:
            QMessageBox.warning(self, '注册失败', '两次输入的密码不一致')
            return
        
        # 验证邮箱验证码
        if not self.verification_code or int(verification_input) != self.verification_code:
            QMessageBox.warning(self, '注册失败', '邮箱验证码错误')
            return
        
        # 创建用户数据
        user_data = {
            'username': username,
            'password': password,
            'userid': userid,
            'phone': phone,
            'email': email
        }
        
        # 调用控制器进行注册
        controller = UserServerController()
        result = controller.adduser_user_ServerStatus(user_data)
        
        if result:
            QMessageBox.information(self, '注册成功', '账户创建成功，请登录')
            self.register_success.emit(username)  # 发送注册成功信号
            self.switch_to_login.emit()  # 切换到登录窗口
        else:
            QMessageBox.warning(self, '注册失败', '用户名已存在或注册失败')