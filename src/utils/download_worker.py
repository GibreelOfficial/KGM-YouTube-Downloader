import os
import sys
import json
from PySide6.QtCore import QThread, Signal, QProcess, QEventLoop
import re

class DownloadWorker(QThread):
    status_updated = Signal(str)
    progress_updated = Signal(float, str)
    video_discovered = Signal(str, str, str)          
    video_status_changed = Signal(str)  

    def __init__(self, url, target_folder, ytdlp_path):
        super().__init__()
        self.url = url
        self.target_folder = target_folder
        self.ytdlp_path = os.path.abspath(ytdlp_path)
        self.process = None

    def run(self):
        self.status_updated.emit("Extracting video information...")
        
        info_process = QProcess()
        info_process.setProgram(self.ytdlp_path)
        
        info_args = ["--dump-json", "--skip-download", "--no-playlist", self.url]
        info_process.setArguments(info_args)
        
        loop = QEventLoop()
        info_process.finished.connect(loop.quit)
        info_process.start()
        loop.exec() 

        if info_process.exitCode() != 0:
            self.status_updated.emit("Error: Could not retrieve video data.")
            return

        try:
            raw_stdout = bytes(info_process.readAllStandardOutput()).decode("utf-8", errors="ignore")
            meta = json.loads(raw_stdout)
            title = meta.get("title", "Unknown Video")
            
            bytes_estimate = meta.get("filesize_approx", meta.get("filesize", 0))
            size_gb = f"{bytes_estimate / (1024**3):.2f} GB" if bytes_estimate else "N/A"
            
            from datetime import datetime
            today_str = datetime.today().strftime('%d %b %Y')
            
            self.video_discovered.emit(title, size_gb, today_str)
            
        except Exception as e:
            self.status_updated.emit(f"Metadata Parsing Error: {str(e)}")
            return

        self.process = QProcess()
        self.process.setProgram(self.ytdlp_path)
        
        output_template = os.path.join(self.target_folder, "%(title)s.%(ext)s")
        bin_directory = os.path.dirname(self.ytdlp_path)
        
        download_args = [
            "-o", output_template,
            "-f", "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]", 
            "--merge-output-format", "mp4",
            "--ffmpeg-location", bin_directory,
            "--newline",
            self.url
        ]
        
        self.process.setArguments(download_args)
        self.process.readyReadStandardOutput.connect(self.handle_output_logs)
        self.process.readyReadStandardError.connect(self.handle_error_logs)
        
        download_loop = QEventLoop()
        self.process.finished.connect(download_loop.quit)
        self.process.start()
        download_loop.exec()

        if self.process.exitCode() == 0:
            self.save_download_to_db(title, size_gb, today_str)
            self.video_status_changed.emit("complete")
            self.status_updated.emit("Status: All downloads completed successfully!")
        else:
            self.video_status_changed.emit("failed")
            self.status_updated.emit("Status: Execution error occurred during download.")

    def handle_output_logs(self):
        raw_output = bytes(self.process.readAllStandardOutput()).decode("utf-8", errors="ignore")
        for line in raw_output.splitlines():
            line_str = line.strip()
            if "[download]" in line_str:
                try:
                    pct_match = re.search(r'(\d+(?:\.\d+)?)%', line_str)
                    if pct_match:
                        pct_val = float(pct_match.group(1))
                        
                    speed_match = re.search(r'at\s+([^\s]+(?:B/s|b/s))', line_str)
                    speed = speed_match.group(1) if speed_match else "---"
                    
                    eta_match = re.search(r'ETA\s+([^\s]+)', line_str)
                    eta = eta_match.group(1) if eta_match else "---"
                    
                    if pct_match:
                        payload = f"PROGRESS_DATA|{speed}|{eta}"
                        self.progress_updated.emit(pct_val, payload)
                except Exception:
                    pass

    def handle_error_logs(self):
        raw_err = bytes(self.process.readAllStandardError()).decode("utf-8", errors="ignore")
        for line in raw_err.splitlines():
            print(f"[DEBUG YTDLP PROCESS STDERR] {line.strip()}")

    def save_download_to_db(self, title, size, date_str):
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "downloads_history.json")
        db_path = os.path.abspath(db_path)
        
        history_data = []
        if os.path.exists(db_path):
            try:
                with open(db_path, "r") as f:
                    history_data = json.load(f)
            except Exception:
                history_data = []
                
        new_record = {
            "title": title,
            "size": size,
            "status": "complete",
            "date": date_str
        }
        history_data.append(new_record)
        
        with open(db_path, "w") as f:
            json.dump(history_data, f, indent=4)