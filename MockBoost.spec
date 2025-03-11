# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['D:\\Project\\MockBoost\\Frame\\main_frame.py'],
    pathex=[],
    binaries=[],
    datas=[('ProjectImages', 'ProjectImages'), ('Frame/objmodel', 'Frame/objmodel'), ('TTSandASR/Model', 'TTSandASR/Model'), ('Training', 'Training'), ('db', 'db')],
    hiddenimports=['PyQt6', 'numpy', 'torch', 'transformers', 'redis', 'uuid', 'json', 'OpenGL', 'db', 'TTSandASR', 'Main', 'Frame'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

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
    icon=['D:\\Project\\MockBoost\\ProjectImages\\Login.png'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='MockBoost',
)
