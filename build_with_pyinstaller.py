import PyInstaller.__main__
import os
import sys

# 获取当前脚本所在目录
base_dir = os.path.dirname(os.path.abspath(__file__))

# 设置图标路径
icon_path = os.path.join(base_dir, 'ProjectImages', 'Login.png')

# 设置主程序路径
main_script = os.path.join(base_dir, 'Frame', 'main_frame.py')

# 设置PyInstaller命令行参数
pyinstaller_args = [
    main_script,
    '--name=MockBoost',
    f'--icon={icon_path}',
    '--windowed',  # 使用GUI模式，不显示控制台
    '--onedir',   # 创建单文件夹模式的可执行文件
    '--clean',    # 清理临时文件
    # 添加数据文件
    '--add-data=ProjectImages;ProjectImages',
    '--add-data=Frame/objmodel;Frame/objmodel',
    '--add-data=TTSandASR/Model;TTSandASR/Model',
    '--add-data=Training;Training',
    '--add-data=db;db',
    # 添加需要包含的模块
    '--hidden-import=PyQt6',
    '--hidden-import=numpy',
    '--hidden-import=torch',
    '--hidden-import=transformers',
    '--hidden-import=redis',
    '--hidden-import=uuid',
    '--hidden-import=json',
    '--hidden-import=OpenGL',
    '--hidden-import=db',
    '--hidden-import=TTSandASR',
    '--hidden-import=Main',
    '--hidden-import=Frame',
]

# 运行PyInstaller
print('开始使用PyInstaller打包应用程序...')
PyInstaller.__main__.run(pyinstaller_args)
print('打包完成！可执行文件位于 dist/MockBoost 目录下')