# -*- mode: python ; coding: utf-8 -*-
import os
import subprocess
from pathlib import Path
import platform
import shutil

app_name = '水印助手'

data_dirs = [
  "AppData/cache",
  "AppData/logs",
  "AppData/exiftool",
  "resource", 
  "app"
]
datas = [
  ("AppData", "AppData"),
  ("resource", "resource"),
  ("app", "app"),
  ("token", "."),
  ("token_inner", "."),
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
    icon=['logo.mac.ico'],
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
  icon='logo.mac.ico',
  bundle_identifier=None,
)

def create_zip():
    """调用系统压缩工具创建ZIP文件（macOS/Unix系统）"""
    dist_dir = Path('dist') / f'{app_name}.app'
    zip_path = Path('dist') / 'watermark-mac.zip'
    
    # 确保输出目录存在
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"Creating {zip_path} using system zip...")
    
    try:
        # macOS系统使用ditto命令（保留元数据和符号链接）
        subprocess.run([
            'ditto',
            '-c', '-k', '--sequesterRsrc', '--keepParent',
            str(dist_dir),
            str(zip_path)
        ], check=True)
        
        print(f"System zip created at {zip_path}")
    except subprocess.CalledProcessError as e:
        print(f"System zip failed: {e}")

create_zip()
subprocess.run(["open", "./dist"])