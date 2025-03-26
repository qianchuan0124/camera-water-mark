# -*- mode: python ; coding: utf-8 -*-
import os
import subprocess
import platform
import shutil

app_name = '水印助手'

data_dirs = [
  "AppData/bin",
  "AppData/cache",
  "AppData/logs",
  "AppData/models",
  "resource", 
  "app"
]
datas = [
  ("AppData", "AppData"),
  ("resource", "resource"),
  ("app", "app"),
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[],
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
    name=app_name,
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
    icon=['logo.ico'],
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=app_name,
)

app = BUNDLE(
  coll,
  name=f'{app_name}.app',
  icon='logo.ico',
  bundle_identifier=None,
)