from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QObject, pyqtSignal
import sys
from login_window import LoginWindow
from main_window import MainWindow

class AppController(QObject):
    """
    应用程序控制器，负责管理窗口之间的切换和用户会话
    """
    def __init__(self):
        super().__init__()
        self.login_window = None
        self.main_window = None
        self.current_username = ""
        
    def start_application(self):
        """
        启动应用程序，显示登录窗口
        """
        self.login_window = LoginWindow()
        # 修改登录窗口的open_main_window方法，使其通知控制器
        self.login_window.open_main_window = self.show_main_window
        self.login_window.show()
    
    def show_main_window(self):
        """
        显示主窗口，关闭登录窗口
        """
        # 获取登录窗口中的用户名
        self.current_username = self.login_window.username_input.text()
        
        # 创建并显示主窗口
        self.main_window = MainWindow(self.current_username)
        # 可以在这里设置主窗口的一些属性，例如传递用户名
        self.main_window.show()
        
        # 关闭登录窗口
        if self.login_window:
            self.login_window.close()
            
    def close_application(self):
        """
        关闭应用程序
        """
        if self.main_window:
            self.main_window.close()
        if self.login_window:
            self.login_window.close()

def main():
    """
    应用程序入口点
    """
    app = QApplication(sys.argv)
    controller = AppController()
    controller.start_application()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()