import os
import sys
import stat
import json
import requests
from PySide6.QtCore import QObject, QThread, Signal

class YTBDLPUpdater(QThread):
    status_updated = Signal(str)
    update_finished = Signal(bool, str)

    def __init__(self, bin_dir):
        super().__init__()
        self.base_bin_dir = os.path.abspath(bin_dir)
        
        platform = sys.platform
        if platform == "win32":
            self.sub_folder = "win32"
        elif platform == "darwin":
            self.sub_folder = "darwin"
        else:
            self.sub_folder = "linux"
            
        self.bin_dir = os.path.join(self.base_bin_dir, self.sub_folder)
        self.repo_url = "https://api.github.com/repos/yt-dlp/yt-dlp/releases/latest"
        self.version_file = os.path.join(self.bin_dir, "version_info.json")

    def get_filenames(self):
        platform = sys.platform
        paths = {}
        if platform == "win32":
            paths["ytdlp_name"] = "yt-dlp.exe"
            paths["ffmpeg_name"] = "ffmpeg.exe"
        elif platform == "darwin":
            paths["ytdlp_name"] = "yt-dlp_macos"
            paths["ffmpeg_name"] = "ffmpeg"
        elif platform.startswith("linux"):
            paths["ytdlp_name"] = "yt-dlp"
            paths["ffmpeg_name"] = "ffmpeg"
        else:
            return None
        return paths

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
        cfg = self.get_filenames()
        if not cfg:
            self.update_finished.emit(False, "Unsupported OS platform.")
            return

        os.makedirs(self.bin_dir, exist_ok=True)
        ytdlp_path = os.path.join(self.bin_dir, cfg["ytdlp_name"])
        ffmpeg_path = os.path.join(self.bin_dir, cfg["ffmpeg_name"])

        if not os.path.exists(ffmpeg_path):
            self.update_finished.emit(False, f"Required dependency missing: {cfg['ffmpeg_name']} must be manually dropped into bin/{self.sub_folder}/")
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

            if not os.path.exists(ytdlp_path) or local_version != remote_version:
                self.status_updated.emit("Updating core backend package components...")
                download_url = None
                for asset in release_data.get("assets", []):
                    if asset.get("name") == cfg["ytdlp_name"]:
                        download_url = asset.get("browser_download_url")
                        break

                if not download_url:
                    self.update_finished.emit(False, f"Could not find assets matching {cfg['ytdlp_name']}.")
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
                    os.chmod(ytdlp_path, st.st_mode | stat.S_IEXEC)

            self.save_local_version(remote_version)
            self.update_finished.emit(True, ytdlp_path)

        except Exception as e:
            self.update_finished.emit(False, str(e))


class YTDLPUpdaterWorker(QObject):
    progress = Signal(str)
    finished = Signal(bool, str)

    def __init__(self, current_binary_path):
        super().__init__()
        self.binary_path = os.path.abspath(current_binary_path)
        self.bin_dir = os.path.dirname(self.binary_path)
        self.repo_url = "https://api.github.com/repos/yt-dlp/yt-dlp/releases/latest"
        self.version_file = os.path.join(self.bin_dir, "version_info.json")

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
        platform = sys.platform
        if platform == "win32":
            ytdlp_name = "yt-dlp.exe"
            ffmpeg_name = "ffmpeg.exe"
        elif platform == "darwin":
            ytdlp_name = "yt-dlp_macos"
            ffmpeg_name = "ffmpeg"
        elif platform.startswith("linux"):
            ytdlp_name = "yt-dlp"
            ffmpeg_name = "ffmpeg"
        else:
            self.finished.emit(False, "Unsupported operating system platform.")
            return

        ffmpeg_path = os.path.join(self.bin_dir, ffmpeg_name)
        if not os.path.exists(ffmpeg_path):
            self.finished.emit(False, f"Muxer execution binary tracking fault: {ffmpeg_name} not found locally.")
            return

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
                if asset.get("name") == ytdlp_name:
                    download_url = asset.get("browser_download_url")
                    break

            if not download_url:
                self.finished.emit(False, f"Could not locate asset package {ytdlp_name}.")
                return

            self.progress.emit(f"Downloading latest server release: {ytdlp_name}...")
            temp_file_path = os.path.join(self.bin_dir, f"{ytdlp_name}.tmp")

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
                os.chmod(self.binary_path, st.st_mode | stat.S_IEXEC)

            self.save_local_version(remote_version)
            self.finished.emit(True, "Update complete! Restructuring environmental execution pipelines...")

        except Exception as e:
            self.finished.emit(False, f"Update sequence failed: {str(e)}")