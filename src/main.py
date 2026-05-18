import sys
import os
import re
import json
import subprocess
from PySide6.QtWidgets import QApplication, QHBoxLayout, QVBoxLayout
from PySide6.QtCore import Qt, QThread, Signal, Slot

from components.framelessWindow import FramelessWindow
from components.main_view import MainContentView
from components.sidebar import Sidebar
from components.statusBar import StatusBar
from utils.theme_loader import load_stylesheet

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class DownloadWorker(QThread):
    progress_updated = Signal(float, str)
    video_discovered = Signal(list)
    status_updated = Signal(str)
    video_status_changed = Signal(int, str)
    finished_all = Signal()

    def __init__(self, url, folder, ytdlp_path):
        super().__init__()
        self.url = url
        self.folder = folder
        self.ytdlp_path = ytdlp_path

    def fetch_video_list(self):
        try:
            result = subprocess.run(
                [self.ytdlp_path, '--flat-playlist', '-J', self.url],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True
            )
            data = json.loads(result.stdout)

            if 'entries' in data:
                entries = data['entries']
                urls = [f"https://www.youtube.com/watch?v={e['id']}" for e in entries if 'id' in e]
                
                titles = []
                for u in urls:
                    info = subprocess.run(
                        [self.ytdlp_path, '-J', u], 
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
                    )
                    if info.returncode == 0:
                        meta = json.loads(info.stdout)
                        titles.append(meta.get("title", u))
                    else:
                        titles.append(u)
                return list(zip(titles, urls))
            else:
                return [(data.get("title", self.url), self.url)]
        except Exception:
            return []

    def run(self):
        self.status_updated.emit("Fetching stream data...")
        video_entries = self.fetch_video_list()
        
        if not video_entries:
            self.status_updated.emit("Error: Could not retrieve video data.")
            self.finished_all.emit()
            return

        self.video_discovered.emit([title for title, _ in video_entries])

        progress_pattern = re.compile(r'\[download\]\s+(\d+\.\d+)%')

        for idx, (title, video_url) in enumerate(video_entries):
            self.video_status_changed.emit(idx, "downloading")
            self.status_updated.emit(f"Downloading: {title}")

            cmd = [
                self.ytdlp_path,
                '-f', 'bestvideo[height<=720]+bestaudio/best[height<=720]',
                '-o', os.path.join(self.folder, '%(title)s.%(ext)s'),
                video_url
            ]

            process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
            )

            while True:
                line = process.stdout.readline()
                if not line:
                    break
                match = progress_pattern.search(line)
                if match:
                    percent = float(match.group(1))
                    self.progress_updated.emit(percent, f"Downloading: {title} - {percent:.1f}%")

            process.wait()

            if process.returncode == 0:
                self.video_status_changed.emit(idx, "success")
            else:
                self.video_status_changed.emit(idx, "failed")
                
            self.progress_updated.emit(0.0, "")

        self.status_updated.emit("All tasks completed successfully.")
        self.finished_all.emit()

class KGMDownloaderApp(FramelessWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KGM YouTube Downloader")
        self.resize(1100, 700)
        self.ytdlp_path = resource_path("yt-dlp")
        self.worker = None
        self.setup_body()

    def setup_body(self):
        central_layout = QHBoxLayout(self.content_area)
        central_layout.setContentsMargins(0, 0, 0, 0)
        central_layout.setSpacing(0)

        self.sidebar = Sidebar(self)
        self.main_content = MainContentView(self)
        
        central_layout.addWidget(self.sidebar)
        central_layout.addWidget(self.main_content, 1)

        self.status_bar = StatusBar(self)
        self.container_layout.addWidget(self.status_bar)

        self.connect_ui_events()

    def connect_ui_events(self):
        pass

    def start_download_process(self, url, target_folder):
        if self.worker and self.worker.isRunning():
            return

        self.worker = DownloadWorker(url, target_folder, self.ytdlp_path)
        
        self.worker.status_updated.connect(self.update_status_message)
        self.worker.progress_updated.connect(self.update_download_progress)
        self.worker.video_discovered.connect(self.populate_queue_list)
        self.worker.video_status_changed.connect(self.update_item_state)
        self.worker.finished_all.connect(self.on_process_finished)
        
        self.worker.start()

    @Slot(str)
    def update_status_message(self, message):
        if hasattr(self.status_bar, 'set_message'):
            self.status_bar.set_message(message)

    @Slot(float, str)
    def update_download_progress(self, percentage, description):
        if hasattr(self.main_content, 'progress_bar'):
            self.main_content.progress_bar.setValue(int(percentage))
        if description:
            self.update_status_message(description)

    @Slot(list)
    def populate_queue_list(self, title_list):
        if hasattr(self.main_content, 'table') and hasattr(self.main_content.table, 'clear_and_fill'):
            self.main_content.table.clear_and_fill(title_list)

    @Slot(int, str)
    def update_item_state(self, index, state):
        if hasattr(self.main_content, 'table') and hasattr(self.main_content.table, 'update_row_status'):
            self.main_content.table.update_row_status(index, state)

    @Slot()
    def on_process_finished(self):
        self.worker = None

    def apply_theme_to_all(self, checked):
        dynamic_color = "#222222" if checked else "#ffffff"
        self.sidebar.update_theme_icons(dynamic_color)
        self.main_content.update_theme_icons(dynamic_color)
        self.status_bar.update_theme_icons(dynamic_color)

def main():
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_EnableHighDpiScaling)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps)

    try:
        app.setStyleSheet(load_stylesheet("dark_neon"))
    except Exception:
        pass

    window = KGMDownloaderApp()
    window.title_bar.theme_toggle.toggled.connect(window.apply_theme_to_all)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()