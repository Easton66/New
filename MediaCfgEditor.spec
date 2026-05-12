# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_all

# 收集 PySide6 的所有子模块、DLL和数据文件
pyside6_datas, pyside6_binaries, pyside6_hiddenimports = collect_all('PySide6')

# 收集核心 Qt 模块的动态库
for qt_mod in ('PySide6.QtCore', 'PySide6.QtGui', 'PySide6.QtWidgets'):
    _, mod_bins, mod_hidden = collect_all(qt_mod)
    pyside6_binaries += mod_bins
    pyside6_hiddenimports += mod_hidden

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=pyside6_binaries,
    datas=[('dropdowns.json', '.')] + pyside6_datas,
    hiddenimports=pyside6_hiddenimports,
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
    a.binaries,
    a.datas,
    [],
    name='MediaCfgEditor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
