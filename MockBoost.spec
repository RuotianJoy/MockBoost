# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# 收集所有必要的数据文件
additional_datas = [
    ('ProjectImages', 'ProjectImages'),  # 图像文件
    ('Email', 'Email'),  # 邮件相关文件
    ('db', 'db'),  # 数据库相关文件
    ('TTSandASR/Model', 'TTSandASR/Model'),  # 语音模型文件
    ('Training/data', 'Training/data'),  # 训练数据
    ('Training/Deepseek', 'Training/Deepseek'),  # Deepseek模型文件
    ('D:\\Anaconda3\\envs\\MockBoostEnv\\Lib\\site-packages', 'site-packages'),  # 所有依赖包
]

# 添加需要排除的模块
excluded_modules = [
    'matplotlib', 'tkinter', 'PySide6', 'IPython', 'jupyter',
    'sphinx', 'pytest', 'test', 'tests', 'testing'
]

a = Analysis(
    ['Frame/main_frame.py'],  # 主入口文件
    pathex=['d:\\Project\\MockBoost', 'd:\\Project\\MockBoost\\Frame'],  # 添加Frame目录到Python路径
    binaries=[],
    datas=additional_datas,
    hiddenimports=[
        'PyQt6.QtCore', 'PyQt6.QtWidgets', 'PyQt6.QtGui',  # PyQt6相关模块
        'langchain', 'langchain.llms', 'langchain.embeddings',  # LangChain相关模块
        'openai', 'numpy', 'pandas',  # AI和数据处理相关模块
        'sounddevice', 'soundfile',  # 音频处理相关模块
        'jieba', 'transformers',  # NLP相关模块
        'vosk', 'pyttsx3',  # 语音识别和合成模块
        'pymilvus', 'redis',  # 数据库相关模块
        'sqlalchemy', 'pymysql',  # 数据库ORM和驱动
        'TTS', 'TTS.api', 'TTS.tts', 'TTS.vocoder',  # TTS相关模块
        'TTS.tts.layers.glow_tts', 'TTS.tts.utils', 'TTS.utils',  # TTS额外模块
        'TTS.tts.models.vits', 'TTS.tts.layers.generic.wavenet',  # TTS VITS和Wavenet模块
        'TTS.tts.layers.vits.networks', 'TTS.tts.configs.vits_config',  # TTS VITS配置和网络
        'transformers.models', 'transformers.tokenization_utils',  # Transformers核心模块
        'langchain.chains', 'langchain.prompts',  # LangChain核心模块
        'vosk.model', 'vosk.recognizer',  # Vosk核心模块
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excluded_modules,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='MockBoost',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='ProjectImages/title.ico',
    onefile=True,  # 让 PyInstaller 生成单个 EXE
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='MockBoost',
)