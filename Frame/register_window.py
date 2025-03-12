import random
import traceback

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal
from db.controller.UserServerController import UserServerController
from Email.get_email_api import send_email

class RegisterWindow(QWidget):
    register_success = pyqtSignal(str)  # 注册成功信号，传递用户名
    switch_to_login = pyqtSignal()  # 切换到登录窗口信号
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle('MockBoost Registration')
        self.setFixedSize(400, 600)  # 增加窗口高度以容纳验证码输入框
        self.verification_code = None  # 存储验证码
        self.email_verified = False  # 邮箱验证状态
        self.setup_ui()
        
    def setup_ui(self):
        # 创建主布局
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # 添加标题
        title = QLabel('Sign up for a new account')
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
        
        # 确认密码输入框
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText('Please confirm your password')
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_input.setStyleSheet('padding: 8px; border: 1px solid #ccc; border-radius: 4px;')
        layout.addWidget(self.confirm_password_input)
        
        # 手机号输入框
        self.job_input = QLineEdit()
        self.job_input.setPlaceholderText('Please enter your intended occupation')
        self.job_input.setStyleSheet('padding: 8px; border: 1px solid #ccc; border-radius: 4px;')
        layout.addWidget(self.job_input)

        self.major_input = QLineEdit()
        self.major_input.setPlaceholderText('Please enter your major')
        self.major_input.setStyleSheet('padding: 8px; border: 1px solid #ccc; border-radius: 4px;')
        layout.addWidget(self.major_input)
        
        # 邮箱输入框和验证按钮的水平布局
        email_layout = QHBoxLayout()
        
        # 邮箱输入框
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText('Please enter your email address')
        self.email_input.setStyleSheet('padding: 8px; border: 1px solid #ccc; border-radius: 4px;')
        email_layout.addWidget(self.email_input)
        
        # 验证按钮
        self.verify_button = QPushButton('Send the code')
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
        self.verification_input.setPlaceholderText('Please enter the code')
        self.verification_input.setStyleSheet('padding: 8px; border: 1px solid #ccc; border-radius: 4px;')
        layout.addWidget(self.verification_input)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        
        # 注册按钮
        register_button = QPushButton('Register')
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
        back_button = QPushButton('Back to login')
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
            QMessageBox.information(self, 'Verification Code Sent', f'Verification code has been sent to {email}, please check your inbox')
            self.verify_button.setEnabled(False)  # 禁用按钮防止重复发送
            self.verify_button.setText('Sent')  # 更新按钮文本
        except Exception as e:
            QMessageBox.warning(self, 'Sending Failed', f'Failed to send verification code: {str(e)}')

    def handle_register(self):
        # 获取输入信息
        username = self.username_input.text()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()
        userid = 'U' + str(random.randint(100001, 999999))
        job = self.job_input.text()
        major = self.major_input.text()
        email = self.email_input.text()
        verification_input = self.verification_input.text()

        # 验证输入
        if not (username and password and confirm_password and userid and major and job and email and verification_input):
            QMessageBox.warning(self, 'Registration Failed', 'Please fill in all fields')
            return

        if password != confirm_password:
            QMessageBox.warning(self, 'Registration Failed', 'Passwords do not match')
            return

        # 验证邮箱验证码
        if not self.verification_code or int(verification_input) != self.verification_code:
            QMessageBox.warning(self, 'Registration Failed', 'Incorrect email verification code')
            return

        # 创建用户数据
        user_data = {
            'Name': username,
            'Password': password,
            'Email': email,
            'Major': major,
            'Job': job,
            'UUID': userid
        }

        try:
            # 调用控制器进行注册
            controller = UserServerController()
            result = controller.adduser_user_ServerStatus(user_data)

            if result:
                QMessageBox.information(self, 'Registration Successful', 'Account created successfully, please log in')
                self.register_success.emit(username)  # 发送注册成功信号
                self.switch_to_login.emit()  # 切换到登录窗口
            else:
                QMessageBox.warning(self, 'Registration Failed', 'Username already exists or registration failed')
        except Exception as e:
            error_msg = f"注册过程中出错: {str(e)}"
            print(error_msg)
            traceback.print_exc()  # 打印详细的堆栈跟踪
            QMessageBox.critical(self, '连接错误', f"无法连接到数据库服务器，请检查网络连接。\n详细信息: {str(e)}")