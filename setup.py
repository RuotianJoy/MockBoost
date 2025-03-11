import sys
import os
from cx_Freeze import setup, Executable

# 添加所有需要包含的模块
build_exe_options = {
    "packages": [
        "PyQt6", "sys", "numpy", "torch", "transformers", "redis", "uuid", "json",
        "OpenGL", "db", "TTSandASR", "Main", "Frame"
    ],
    "include_files": [
        # 添加需要包含的资源文件和目录
        ("ProjectImages", "ProjectImages"),
        ("Frame/objmodel", "Frame/objmodel"),
        ("TTSandASR/Model", "TTSandASR/Model"),
        ("Training", "Training"),
        ("db", "db")
    ],
    "excludes": ["tkinter", "unittest"],
    "include_msvcr": True,
}

# 设置基本信息
base = None
if sys.platform == "win32":
    base = "Win32GUI"  # 使用Windows GUI应用程序

# 设置可执行文件
executables = [
    Executable(
        "Frame/main_frame.py",  # 主程序入口
        base=base,
        target_name="MockBoost.exe",  # 生成的可执行文件名
        icon="ProjectImages/Login.png",  # 应用图标
        shortcut_name="MockBoost",
        shortcut_dir="DesktopFolder"
    )
]

# 设置安装程序
setup(
    name="MockBoost",
    version="1.0.0",
    description="MockBoost - AI面试助手",
    options={"build_exe": build_exe_options},
    executables=executables
)