# -*- mode: python ; coding: utf-8 -*-
import os

block_cipher = None

yt_dlp_path = os.path.join('bin', 'yt-dlp')  # Adjust if your binary path differs

a = Analysis(
    ['main.py'],
    pathex=[os.getcwd()],
    binaries=[(yt_dlp_path, '.')],  # Include yt-dlp in the root of the app bundle
    datas=[('graphiti.png', '.')],  # Include your background image
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    noarchive=False
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='KGM YouTube Downloader',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=True,  # macOS .app support
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.icns'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='KGM YouTube Downloader'
)

app = BUNDLE(
    coll,
    name='KGM YouTube Downloader.app',
    icon='icon.icns',
    info_plist='Info.plist'
)
