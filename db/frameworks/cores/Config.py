import configparser
import os
import socket
import platform

class Config:
    conf = ""

    def __init__(self):
        sys_platform = platform.platform().lower()
        print(sys_platform)

        cfgpath = os.path.abspath("../db/configs/machine.ini")

        print("Config path: ", cfgpath)

        config = configparser.ConfigParser()

        # 创建管理对象
        self.conf = configparser.ConfigParser()

        # 读ini文件
        self.conf.read(cfgpath, encoding="utf-8")  # python3

    def getDB(self):
        return [self.conf.get("UserInfo", "host"),
                self.conf.get("UserInfo", "user"),
                self.conf.get("UserInfo", "pass"),
                self.conf.getint("UserInfo", "port"),
                self.conf.get("UserInfo", "dbname")
                ]

    def getOcsOnline(self):
        return [self.conf.get("UserInfo","host"),
                self.conf.get("UserInfo","user"),
                self.conf.get("UserInfo","pass"),
                self.conf.getint("UserInfo","port"),
                self.conf.get("UserInfo","dbname")
                ]