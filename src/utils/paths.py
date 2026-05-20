import os
import sys

if hasattr(sys, '_MEIPASS'):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ASSETS_DIR = os.path.join(BASE_DIR, "assets")

def get_platform_subfolder():
    if sys.platform == "win32":
        return "win32"
    elif sys.platform == "darwin":
        return "darwin"
    return "linux"

def get_binary_names():
    if sys.platform == "win32":
        return {"ytdlp": "yt-dlp.exe", "ffmpeg": "ffmpeg.exe"}
    return {"ytdlp": "yt-dlp", "ffmpeg": "ffmpeg"}

def get_secure_storage_dir():
    if sys.platform == "win32":
        base_dir = os.getenv("APPDATA")
    elif sys.platform == "darwin":
        base_dir = os.path.expanduser("~/Library/Application Support")
    else:
        base_dir = os.path.expanduser("~/.local/share")
        
    app_storage = os.path.join(base_dir, "KGM_YouTube_Downloader", "bin")
    os.makedirs(app_storage, exist_ok=True)
    return app_storage

PLATFORM_SUBFOLDER = get_platform_subfolder()
names = get_binary_names()
YTDLP_FILENAME = names["ytdlp"]
FFMPEG_FILENAME = names["ffmpeg"]

if hasattr(sys, '_MEIPASS'):
    FALLBACK_BIN_DIR = os.path.join(BASE_DIR, "bin", PLATFORM_SUBFOLDER)
else:
    FALLBACK_BIN_DIR = os.path.join(BASE_DIR, "src", "bin", PLATFORM_SUBFOLDER)

ACTIVE_BIN_DIR = get_secure_storage_dir()

YTDLP_PATH = os.path.join(ACTIVE_BIN_DIR, YTDLP_FILENAME)
if not os.path.exists(YTDLP_PATH):
    fallback_ytdlp = os.path.join(FALLBACK_BIN_DIR, YTDLP_FILENAME)
    if os.path.exists(fallback_ytdlp):
        YTDLP_PATH = fallback_ytdlp

FFMPEG_PATH = os.path.join(ACTIVE_BIN_DIR, FFMPEG_FILENAME)
if not os.path.exists(FFMPEG_PATH):
    fallback_ffmpeg = os.path.join(FALLBACK_BIN_DIR, FFMPEG_FILENAME)
    if os.path.exists(fallback_ffmpeg):
        FFMPEG_PATH = fallback_ffmpeg