import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import subprocess
import os
import re
import json
from PIL import Image, ImageTk
import sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and PyInstaller bundles """
    try:
        base_path = sys._MEIPASS  # PyInstaller temp folder
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class YouTubeDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("KGM YouTube Downloader")
        self.root.geometry("500x500")
        self.root.resizable(False, False)

        self.url_var = tk.StringVar()
        self.video_entries = []  # (title, url)

        # Background Canvas
        self.canvas = tk.Canvas(root, width=500, height=500)
        self.canvas.pack(fill="both", expand=True)
        self.bg_image = Image.open(resource_path("graphiti.png"))
        self.bg_image = self.bg_image.resize((500, 500), Image.Resampling.LANCZOS)
        self.bg_photo = ImageTk.PhotoImage(self.bg_image)
        self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")

        # URL Entry
        self.entry = tk.Entry(root, textvariable=self.url_var, width=30)
        self.canvas.create_window(250, 40, window=self.entry)

        self.download_button = tk.Button(root, text="Download 720p", command=self.download)
        self.canvas.create_window(250, 80, window=self.download_button)

        # Progress Bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(root, variable=self.progress_var, maximum=100, length=400)
        self.canvas.create_window(250, 120, window=self.progress_bar)

        self.status_label = tk.Label(root, text="", fg="green", bg="black")
        self.canvas.create_window(250, 150, window=self.status_label)

        # Listbox for videos
        self.list_frame = tk.Frame(root, bg="#000000", bd=0, highlightthickness=0)
        self.list_frame.place(x=50, y=200, width=400, height=250)

        self.video_listbox = tk.Listbox(
            self.list_frame,
            width=60,
            height=12,
            bg="#000000",
            fg="white",
            relief="flat",
            highlightthickness=0
        )
        self.scrollbar = tk.Scrollbar(self.list_frame, orient="vertical", command=self.video_listbox.yview)
        self.video_listbox.config(yscrollcommand=self.scrollbar.set)

        self.video_listbox.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Path to bundled yt-dlp binary
        self.ytdlp_path = resource_path("yt-dlp")

        # Ensure yt-dlp is executable (just in case)
        if os.name == 'posix' and os.path.exists(self.ytdlp_path):
            os.chmod(self.ytdlp_path, 0o755)

    def fetch_video_list(self, url):
        try:
            result = subprocess.run(
                [self.ytdlp_path, '--flat-playlist', '-J', url],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            data = json.loads(result.stdout)

            if 'entries' in data:
                entries = data['entries']
                video_ids = [entry['id'] for entry in entries]
                urls = [f"https://www.youtube.com/watch?v={vid}" for vid in video_ids]

                titles = []
                for u in urls:
                    info = subprocess.run(
                        [self.ytdlp_path, '-J', u],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                    meta = json.loads(info.stdout)
                    titles.append(meta.get("title", u))
                return list(zip(titles, urls))
            else:
                meta = json.loads(result.stdout)
                return [(meta.get("title", url), url)]

        except Exception as e:
            messagebox.showerror("Error", f"Could not fetch video info.\n{e}")
            return []

    def download(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a valid URL.")
            return

        folder = filedialog.askdirectory()
        if not folder:
            return

        def task():
            self.video_listbox.delete(0, tk.END)
            self.video_entries = self.fetch_video_list(url)

            for title, _ in self.video_entries:
                self.video_listbox.insert(tk.END, f"⏳ {title}")

            for idx, (title, video_url) in enumerate(self.video_entries):
                self.video_listbox.delete(idx)
                self.video_listbox.insert(idx, f"⬇ {title}")
                self.video_listbox.select_clear(0, tk.END)
                self.video_listbox.select_set(idx)
                self.video_listbox.activate(idx)
                self.progress_var.set(0)
                self.status_label.config(text=f"Downloading: {title}")

                cmd = [
                    self.ytdlp_path,
                    '-f', 'bestvideo[height<=720]+bestaudio/best[height<=720]',
                    '-o', os.path.join(folder, '%(title)s.%(ext)s'),
                    video_url
                ]

                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                progress_pattern = re.compile(r'\[download\]\s+(\d+\.\d+)%')

                for line in process.stdout:
                    match = progress_pattern.search(line)
                    if match:
                        percent = float(match.group(1))
                        self.progress_var.set(percent)
                        self.status_label.config(text=f"Downloading: {title} - {percent:.1f}%")
                        self.root.update_idletasks()

                process.wait()

                if process.returncode == 0:
                    self.video_listbox.delete(idx)
                    self.video_listbox.insert(idx, f"✔ {title}")
                else:
                    self.video_listbox.delete(idx)
                    self.video_listbox.insert(idx, f"❌ {title}")
                self.progress_var.set(0)

            self.status_label.config(text="All downloads complete.")

        threading.Thread(target=task, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeDownloaderApp(root)
    root.mainloop()
