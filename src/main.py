import sys
import os
import json
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QFileDialog, QMessageBox, 
                             QVBoxLayout, QLabel, QProgressBar, QWidget)
from PySide6.QtCore import Qt, Slot, QThread, QProcess, QSize
from PySide6.QtGui import QMovie
from utils.paths import ASSETS_DIR, FALLBACK_BIN_DIR, YTDLP_PATH
from components.framelessWindow import FramelessWindow
from components.main_view import MainContentView
from components.statusBar import StatusBar
from components.dialogues import QueueWindow
from components.about import AboutDialog
from utils.theme_loader import load_stylesheet
from utils.download_worker import DownloadWorker
from utils.updater import YTBDLPUpdater, YTDLPUpdaterWorker

class UpdateProgressPopup(FramelessWindow):
    def __init__(self, parent=None):
        super().__init__()
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowTitle("Updating Engine")
        self.resize(400, 260)
        
        self.title_bar.theme_toggle.setVisible(False)
        self.title_bar.btn_min.setVisible(False)
        self.title_bar.btn_max.setVisible(False)
        self.title_bar.btn_close.setVisible(False)
        
        body_layout = QVBoxLayout(self.content_area)
        body_layout.setContentsMargins(25, 20, 25, 20)
        body_layout.setSpacing(15)
        
        self.gif_label = QLabel()
        self.gif_label.setAlignment(Qt.AlignCenter)
        
        gif_path = os.path.join(ASSETS_DIR, "dancing.gif")
        self.movie = QMovie(gif_path)
        self.movie.setScaledSize(QSize(120, 120))
        self.gif_label.setFixedSize(120, 120)
        self.gif_label.setMovie(self.movie)
        self.movie.start()
        
        self.info_label = QLabel("Initializing update...")
        self.info_label.setObjectName("detailName")
        self.info_label.setWordWrap(True)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setFixedHeight(12)
        self.progress_bar.setTextVisible(False)
        
        body_layout.addWidget(self.gif_label, 0, Qt.AlignCenter)
        body_layout.addWidget(self.info_label)
        body_layout.addWidget(self.progress_bar)

class KGMDownloaderApp(FramelessWindow):
    def __init__(self, initial_theme="dark_neon"):
        super().__init__()
        self.setWindowTitle("KGM YouTube Downloader")
        self.resize(1050, 680)
        
        self.worker = None
        self.current_theme = initial_theme
        self.queue_dialog = None
        self.about_dialog = None
        
        self.updater_thread = None
        self.updater_worker = None
        self.popup_dialog = None
        
        self.setup_body()
        self.run_background_updater()

    def setup_body(self):
        central_layout = QHBoxLayout(self.content_area)
        central_layout.setContentsMargins(0, 0, 0, 0)
        central_layout.setSpacing(0)

        self.main_content = MainContentView(self)
        central_layout.addWidget(self.main_content, 1)

        self.status_bar = StatusBar(self)
        self.container_layout.addWidget(self.status_bar)

        self.connect_ui_events()

    def connect_ui_events(self):
        self.main_content.add_url_btn.clicked.connect(self.handle_fetch_trigger)
        self.main_content.browse_btn.clicked.connect(self.handle_browse_trigger)
        self.main_content.queue_window_btn.clicked.connect(self.toggle_queue_window)
        self.status_bar.update_btn.clicked.connect(self.trigger_manual_update)
        self.status_bar.about_btn.clicked.connect(self.show_about_dialog)

    def run_background_updater(self):
        self.background_updater = YTBDLPUpdater()
        self.background_updater.status_updated.connect(self.update_status_message)
        self.background_updater.update_finished.connect(self.handle_updater_complete)
        self.background_updater.start()

    @Slot(bool, str)
    def handle_updater_complete(self, success, result_path):
        if success:
            self.update_status_message("Engine verified and updated to local architecture.")
        else:
            self.update_status_message("Engine status verified.")

    @Slot()
    def trigger_manual_update(self):
        self.status_bar.update_btn.setEnabled(False)
        
        self.popup_dialog = UpdateProgressPopup(self)
        self.popup_dialog.show()
        
        self.updater_thread = QThread()
        self.updater_worker = YTDLPUpdaterWorker()
        self.updater_worker.moveToThread(self.updater_thread)
        
        self.updater_thread.started.connect(self.updater_worker.run)
        self.updater_worker.progress.connect(self.handle_manual_update_progress)
        self.updater_worker.finished.connect(self.handle_manual_update_finished)
        
        self.updater_worker.finished.connect(self.updater_thread.quit)
        self.updater_worker.finished.connect(self.updater_worker.deleteLater)
        self.updater_thread.finished.connect(self.updater_thread.deleteLater)
        
        self.updater_thread.start()

    @Slot(str)
    def handle_manual_update_progress(self, message):
        self.update_status_message(message)
        if self.popup_dialog:
            self.popup_dialog.info_label.setText(message)

    @Slot(bool, str)
    def handle_manual_update_finished(self, success, message):
        self.update_status_message(message)
        self.status_bar.update_btn.setEnabled(True)
        
        if self.popup_dialog:
            self.popup_dialog.close()
            self.popup_dialog = None
            
        if success:
            QApplication.quit()
            QProcess.startDetached(sys.executable, sys.argv)
        else:
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Update Failed")
            msg_box.setText(f"Could not complete engine replacement:\n{message}")
            msg_box.setIcon(QMessageBox.Critical)
            msg_box.setStyleSheet(QApplication.instance().styleSheet())
            msg_box.exec()

    @Slot()
    def handle_browse_trigger(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Download Directory")
        if folder:
            self.main_content.detail_path.setText(folder)

    @Slot()
    def handle_fetch_trigger(self):
        url = self.main_content.url_input.text().strip()
        if not url:
            self.update_status_message("Error: Please paste a valid URL link first.")
            return

        folder = self.main_content.detail_path.text()
        if not os.path.isdir(folder):
            folder = os.path.expanduser("~/Downloads")
            self.main_content.detail_path.setText(folder)

        self.start_download_process(url, folder)

    @Slot()
    def toggle_queue_window(self):
        if self.queue_dialog is None:
            self.queue_dialog = QueueWindow(self)
            self.queue_dialog.title_bar.theme_toggle.setVisible(False)
            
        if self.queue_dialog.isVisible():
            self.queue_dialog.hide()
        else:
            self.queue_dialog.show()

    @Slot()
    def show_about_dialog(self):
        self.about_dialog = AboutDialog(self)
        self.about_dialog.show()

    def start_download_process(self, url, target_folder):
        if self.worker and self.worker.isRunning():
            return

        self.worker = DownloadWorker(url, target_folder)
        self.worker.status_updated.connect(self.update_status_message)
        self.worker.progress_updated.connect(self.update_download_progress)
        
        self.worker.video_discovered.connect(self.main_content.handle_download_started)
        self.worker.video_status_changed.connect(self.main_content.handle_download_finished)
        
        self.worker.finished.connect(self.on_process_finished)
        self.worker.start()

    @Slot(str)
    def update_status_message(self, message):
        if hasattr(self.status_bar, 'set_message'):
            self.status_bar.set_message(message)
        elif hasattr(self.status_bar, 'status_label'):
            self.status_bar.status_label.setText(message)

    @Slot(float, str)
    def update_download_progress(self, percentage, description):
        self.main_content.update_active_progress(percentage, description)

    @Slot()
    def on_process_finished(self):
        self.worker = None

    def apply_theme_to_all(self, checked):
        next_theme = "light_neon" if checked else "dark_neon"
        self.current_theme = next_theme
        
        try:
            style_sheet = load_stylesheet(next_theme)
            QApplication.instance().setStyleSheet(style_sheet)
            
            if hasattr(sys, '_MEIPASS'):
                base_path = sys._MEIPASS
            else:
                base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
                
            json_path = os.path.join(base_path, "src" if not hasattr(sys, '_MEIPASS') else "", "themes", f"{next_theme}.json")
            with open(json_path, 'r') as f:
                colors = json.load(f)
                
            dynamic_text_color = colors.get("text_main", "#ffffff")
            
            self.main_content.update_theme_icons(dynamic_text_color)
            self.status_bar.update_theme_icons(dynamic_text_color)
            
            if self.queue_dialog and self.queue_dialog.isVisible():
                self.queue_dialog.update_queue_theme_icons(dynamic_text_color)
        except Exception:
            pass

def main():
    app = QApplication(sys.argv)

    initial_theme = "dark_neon"
    try:
        app.setStyleSheet(load_stylesheet(initial_theme))
    except Exception:
        pass

    window = KGMDownloaderApp(initial_theme)
    window.title_bar.theme_toggle.toggled.connect(window.apply_theme_to_all)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()