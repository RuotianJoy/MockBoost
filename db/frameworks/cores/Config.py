import configparser
import os
import socket
import platform

class Config:
    conf = ""

    def __init__(self):
        sys_platform = platform.platform().lower()
        print(sys_platform)

        # 使用更可靠的路径解析方式
        # 获取当前文件的绝对路径
        current_file = os.path.abspath(__file__)
        # 获取当前文件所在的目录
        current_dir = os.path.dirname(current_file)
        # 构建配置文件的绝对路径
        cfgpath = os.path.join(os.path.dirname(os.path.dirname(current_dir)), "configs", "machine.ini")

        # 如果配置文件不存在，尝试使用相对于执行目录的路径
        if not os.path.exists(cfgpath):
            base_dir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            cfgpath = os.path.join(base_dir, "db", "configs", "machine.ini")
            
        # 如果仍然不存在，尝试使用相对于当前工作目录的路径
        if not os.path.exists(cfgpath):
            cfgpath = os.path.abspath(os.path.join("db", "configs", "machine.ini"))

        print("Config path: ", cfgpath)

        # 创建管理对象
        self.conf = configparser.ConfigParser()

        # 读ini文件
        try:
            self.conf.read(cfgpath, encoding="utf-8")  # python3
            print("配置文件读取成功")
        except Exception as e:
            print(f"配置文件读取失败: {str(e)}")

    def getDB(self):
        try:
            return [self.conf.get("UserInfo", "host"),
                    self.conf.get("UserInfo", "user"),
                    self.conf.get("UserInfo", "pass"),
                    self.conf.getint("UserInfo", "port"),
                    self.conf.get("UserInfo", "dbname")
                    ]
        except Exception as e:
            print(f"获取数据库配置失败: {str(e)}")
            # 返回默认配置
            return ["gz-cynosdbmysql-grp-53cuswb9.sql.tencentcdb.com",
                    "Ljy",
                    "Liao031221!",
                    26837,
                    "UserInfo"]

    def getOcsOnline(self):
        try:
            return [self.conf.get("UserInfo","host"),
                    self.conf.get("UserInfo","user"),
                    self.conf.get("UserInfo","pass"),
                    self.conf.getint("UserInfo","port"),
                    self.conf.get("UserInfo","dbname")
                    ]
        except Exception as e:
            print(f"获取在线配置失败: {str(e)}")
            # 返回默认配置
            return ["gz-cynosdbmysql-grp-53cuswb9.sql.tencentcdb.com",
                    "Ljy",
                    "Liao031221!",
                    26837,
                    "UserInfo"]