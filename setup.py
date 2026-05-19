import os
from setuptools import setup

APP = ['src/main.py']

# Establish absolute reference to the root directory of your project
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

ICON_PATH = os.path.join(BASE_DIR, 'assets', 'logo.icns')
GIF_PATH = os.path.join(BASE_DIR, 'assets', 'dancing.gif')
PNG_PATH = os.path.join(BASE_DIR, 'assets', 'logo.png')

DATA_FILES = [
    ('assets', [GIF_PATH, PNG_PATH]),
]

BIN_DIR = os.path.join(BASE_DIR, 'src', 'bin')
if os.path.exists(BIN_DIR):
    for root, dirs, files in os.walk(BIN_DIR):
        for file in files:
            source_path = os.path.join(root, file)
            rel_path = os.path.relpath(root, os.path.join(BASE_DIR, 'src'))
            DATA_FILES.append((rel_path, [source_path]))

OPTIONS = {
    'argv_emulation': False,
    'iconfile': ICON_PATH,
    'includes': ['PySide6.QtCore', 'PySide6.QtWidgets', 'PySide6.QtGui', 'qtawesome'],
    'packages': ['utils', 'components','themes'],
    'plist': {
        'LSBackgroundOnly': False,
        'CFBundleDevelopmentRegion': 'English',
        'CFBundleIdentifier': 'com.kgm.youtubedownloader',
        'CFBundleVersion': '2.0.0',
        'CFBundleShortVersionString': '2.0.0',
    }
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)