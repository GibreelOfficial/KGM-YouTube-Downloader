import os
import sys
import stat
import json
import requests
from PySide6.QtCore import QObject, QThread, Signal

def get_secure_storage_bin_dir():
    if sys.platform == "win32":
        base_dir = os.getenv("APPDATA")
    elif sys.platform == "darwin":
        base_dir = os.path.expanduser("~/Library/Application Support")
    else:
        base_dir = os.path.expanduser("~/.local/share")
        
    app_storage = os.path.join(base_dir, "KGM_YouTube_Downloader", "bin")
    os.makedirs(app_storage, exist_ok=True)
    return app_storage

class YTBDLPUpdater(QThread):
    status_updated = Signal(str)
    update_finished = Signal(bool, str)

    def __init__(self, fallback_bin_dir):
        super().__init__()
        self.bin_dir = get_secure_storage_bin_dir()
        self.fallback_bin_dir = os.path.abspath(fallback_bin_dir)
        self.repo_url = "https://api.github.com/repos/yt-dlp/yt-dlp/releases/latest"
        self.version_file = os.path.join(self.bin_dir, "version_info.json")

    def get_platform_filenames(self):
        platform = sys.platform
        cfg = {}
        if platform == "win32":
            cfg["remote_name"] = "yt-dlp.exe"
            cfg["local_name"] = "yt-dlp.exe"
            cfg["ffmpeg_name"] = "ffmpeg.exe"
        elif platform == "darwin":
            cfg["remote_name"] = "yt-dlp_macos"
            cfg["local_name"] = "yt-dlp_macos"
            cfg["ffmpeg_name"] = "ffmpeg"
        else:
            cfg["remote_name"] = "yt-dlp"
            cfg["local_name"] = "yt-dlp"
            cfg["ffmpeg_name"] = "ffmpeg"
        return cfg

    def get_local_version(self):
        if os.path.exists(self.version_file):
            try:
                with open(self.version_file, "r") as f:
                    data = json.load(f)
                    return data.get("yt-dlp-version")
            except Exception:
                return None
        return None

    def save_local_version(self, version_tag):
        try:
            with open(self.version_file, "w") as f:
                json.dump({"yt-dlp-version": version_tag}, f, indent=4)
        except Exception:
            pass

    def run(self):
        cfg = self.get_platform_filenames()
        ytdlp_path = os.path.join(self.bin_dir, cfg["local_name"])
        ffmpeg_path = os.path.join(self.bin_dir, cfg["ffmpeg_name"])

        if not os.path.exists(ffmpeg_path):
            fallback_ffmpeg = os.path.join(self.fallback_bin_dir, cfg["ffmpeg_name"])
            if os.path.exists(fallback_ffmpeg):
                import shutil
                try:
                    shutil.copy2(fallback_ffmpeg, ffmpeg_path)
                    if sys.platform != "win32":
                        os.chmod(ffmpeg_path, os.stat(ffmpeg_path).st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
                except Exception as e:
                    self.update_finished.emit(False, f"Failed initializing backend binaries: {str(e)}")
                    return
            else:
                self.update_finished.emit(False, f"Required core dependency missing: {cfg['ffmpeg_name']}")
                return

        try:
            self.status_updated.emit("Checking engine configuration status...")
            response = requests.get(self.repo_url, timeout=15)
            response.raise_for_status()
            release_data = response.json()
            remote_version = release_data.get("tag_name")

            local_version = self.get_local_version()

            if os.path.exists(ytdlp_path) and local_version == remote_version:
                self.update_finished.emit(False, ytdlp_path)
                return

            self.status_updated.emit("Updating core backend package components...")
            download_url = None
            for asset in release_data.get("assets", []):
                if asset.get("name") == cfg["remote_name"]:
                    download_url = asset.get("browser_download_url")
                    break

            if not download_url:
                self.update_finished.emit(False, f"Could not find assets matching remote framework requirements.")
                return

            temp_ytdlp = ytdlp_path + ".tmp"
            with requests.get(download_url, stream=True, timeout=30) as r:
                r.raise_for_status()
                with open(temp_ytdlp, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            
            if os.path.exists(ytdlp_path):
                os.remove(ytdlp_path)
            os.rename(temp_ytdlp, ytdlp_path)
            
            if sys.platform != "win32":
                st = os.stat(ytdlp_path)
                os.chmod(ytdlp_path, st.st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)

            self.save_local_version(remote_version)
            self.update_finished.emit(True, ytdlp_path)

        except Exception as e:
            self.update_finished.emit(False, str(e))


class YTDLPUpdaterWorker(QObject):
    progress = Signal(str)
    finished = Signal(bool, str)

    def __init__(self, current_binary_path):
        super().__init__()
        self.bin_dir = get_secure_storage_bin_dir()
        cfg = self.get_platform_filenames()
        self.binary_path = os.path.join(self.bin_dir, cfg["local_name"])
        self.repo_url = "https://api.github.com/repos/yt-dlp/yt-dlp/releases/latest"
        self.version_file = os.path.join(self.bin_dir, "version_info.json")

    def get_platform_filenames(self):
        platform = sys.platform
        cfg = {}
        if platform == "win32":
            cfg["remote_name"] = "yt-dlp.exe"
            cfg["local_name"] = "yt-dlp.exe"
        elif platform == "darwin":
            cfg["remote_name"] = "yt-dlp_macos"
            cfg["local_name"] = "yt-dlp"
        else:
            cfg["remote_name"] = "yt-dlp"
            cfg["local_name"] = "yt-dlp"
        return cfg

    def get_local_version(self):
        if os.path.exists(self.version_file):
            try:
                with open(self.version_file, "r") as f:
                    data = json.load(f)
                    return data.get("yt-dlp-version")
            except Exception:
                return None
        return None

    def save_local_version(self, version_tag):
        try:
            with open(self.version_file, "w") as f:
                json.dump({"yt-dlp-version": version_tag}, f, indent=4)
        except Exception:
            pass

    def run(self):
        cfg = self.get_platform_filenames()
        self.progress.emit("Checking repository frameworks for component updates...")
        try:
            response = requests.get(self.repo_url, timeout=15)
            response.raise_for_status()
            release_data = response.json()
            remote_version = release_data.get("tag_name")

            local_version = self.get_local_version()

            if os.path.exists(self.binary_path) and local_version == remote_version:
                self.finished.emit(False, "Engine optimization target is already completely up to date.")
                return

            download_url = None
            for asset in release_data.get("assets", []):
                if asset.get("name") == cfg["remote_name"]:
                    download_url = asset.get("browser_download_url")
                    break

            if not download_url:
                self.finished.emit(False, f"Could not locate asset package matching remote configuration requirements.")
                return

            self.progress.emit(f"Downloading latest server release: {cfg['remote_name']}...")
            temp_file_path = self.binary_path + ".tmp"

            with requests.get(download_url, stream=True, timeout=30) as r:
                r.raise_for_status()
                with open(temp_file_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)

            self.progress.emit("Replacing outdated executable engine component...")
            if os.path.exists(self.binary_path):
                try:
                    os.remove(self.binary_path)
                except OSError:
                    backup_path = self.binary_path + ".old"
                    if os.path.exists(backup_path):
                        os.remove(backup_path)
                    os.rename(self.binary_path, backup_path)

            os.rename(temp_file_path, self.binary_path)

            if sys.platform != "win32":
                st = os.stat(self.binary_path)
                os.chmod(self.binary_path, st.st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)

            self.save_local_version(remote_version)
            self.finished.emit(True, "Update complete! Restructuring environmental execution pipelines...")

        except Exception as e:
            self.finished.emit(False, f"Update sequence failed: {str(e)}")