#!/usr/bin/env python3
"""
FLARE DOWNLOAD - Multi-Platform Video Downloader
Clean. Cinematic. Fast.
"""

import sys
import os

# Dependency check
def check_dependencies():
    errors = []
    try:
        import tkinter
    except ImportError:
        errors.append("tkinter not installed - reinstall Python with tcl/tk")
    try:
        import customtkinter
    except ImportError:
        errors.append("customtkinter not installed - run: pip install customtkinter")
    try:
        import yt_dlp
    except ImportError:
        errors.append("yt-dlp not installed - run: pip install yt-dlp")
    if errors:
        print("Missing dependencies:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)

check_dependencies()

import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import subprocess
import math
from typing import Optional
import yt_dlp

try:
    from version import __version__, GITHUB_REPO
except ImportError:
    __version__ = "2.8.3"
    GITHUB_REPO = "contactmukundthiru-cyber/Multi-Platform-Downloader"

try:
    from updater import Updater
    HAS_UPDATER = True
except ImportError:
    HAS_UPDATER = False

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


# Flare color palette
class Colors:
    BLACK = "#000000"
    BG = "#0a0a0a"
    SURFACE = "#111111"
    SURFACE_LIGHT = "#1a1a1a"
    BORDER = "#2a2a2a"
    FIRE = "#ff4500"
    FIRE_DIM = "#cc3700"
    FIRE_GLOW = "#ff6633"
    WHITE = "#ffffff"
    GRAY = "#888888"
    GRAY_DIM = "#555555"
    SUCCESS = "#00cc66"
    ERROR = "#ff3333"


class FlareDownloadApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window
        self.title("Flare Download")
        self.geometry("750x850")
        self.minsize(650, 750)
        self.configure(fg_color=Colors.BLACK)

        # State
        self.is_downloading = False
        self._glow_phase = 0

        # Variables
        self.url_var = ctk.StringVar()
        self.output_dir = ctk.StringVar(value=self._get_default_download_dir())
        self.format_var = ctk.StringVar(value="mp4")
        self.quality_var = ctk.StringVar(value="Best")
        self.media_type = ctk.StringVar(value="Video")

        self.video_formats = ["mp4", "webm", "mkv", "mov", "avi"]
        self.audio_formats = ["mp3", "m4a", "wav", "flac", "opus"]
        self.video_qualities = ["Best", "1080p", "720p", "480p", "360p"]
        self.audio_qualities = ["Best", "320k", "256k", "192k", "128k"]

        self._build_ui()
        self._start_glow_animation()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _get_default_download_dir(self) -> str:
        downloads = os.path.expanduser("~/Downloads")
        return downloads if os.path.isdir(downloads) else os.path.expanduser("~")

    def _build_ui(self):
        # Main container
        main = ctk.CTkFrame(self, fg_color=Colors.BLACK)
        main.pack(fill="both", expand=True, padx=40, pady=40)

        # ═══════════════════════════════════════════════════════════════════
        # HEADER - Cinematic title
        # ═══════════════════════════════════════════════════════════════════
        header = ctk.CTkFrame(main, fg_color="transparent")
        header.pack(fill="x", pady=(0, 35))

        # Fire accent bar
        accent = ctk.CTkFrame(header, fg_color=Colors.FIRE, height=3, corner_radius=0)
        accent.pack(fill="x", pady=(0, 20))

        # Title
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(fill="x")

        ctk.CTkLabel(
            title_frame,
            text="FLARE",
            font=ctk.CTkFont(family="Arial Black", size=48, weight="bold"),
            text_color=Colors.WHITE
        ).pack(side="left")

        ctk.CTkLabel(
            title_frame,
            text="DOWNLOAD",
            font=ctk.CTkFont(family="Arial", size=18, weight="bold"),
            text_color=Colors.FIRE
        ).pack(side="left", padx=(15, 0), pady=(18, 0))

        ctk.CTkLabel(
            title_frame,
            text=f"v{__version__}",
            font=ctk.CTkFont(size=11),
            text_color=Colors.GRAY_DIM
        ).pack(side="right", pady=(20, 0))

        # Tagline
        ctk.CTkLabel(
            header,
            text="YouTube  ·  TikTok  ·  Instagram  ·  Twitter  ·  1000+ sites",
            font=ctk.CTkFont(size=12),
            text_color=Colors.GRAY_DIM
        ).pack(anchor="w", pady=(15, 0))

        # ═══════════════════════════════════════════════════════════════════
        # URL INPUT
        # ═══════════════════════════════════════════════════════════════════
        url_section = ctk.CTkFrame(main, fg_color=Colors.SURFACE, corner_radius=12)
        url_section.pack(fill="x", pady=(0, 20))

        # Section label with accent
        label_row = ctk.CTkFrame(url_section, fg_color="transparent")
        label_row.pack(fill="x", padx=20, pady=(18, 12))

        ctk.CTkFrame(label_row, fg_color=Colors.FIRE, width=4, height=16, corner_radius=0).pack(side="left")
        ctk.CTkLabel(
            label_row,
            text="VIDEO URL",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=Colors.GRAY
        ).pack(side="left", padx=(12, 0))

        # URL Entry
        self.url_entry = ctk.CTkEntry(
            url_section,
            textvariable=self.url_var,
            placeholder_text="Paste video URL here...",
            height=50,
            corner_radius=8,
            border_width=2,
            border_color=Colors.BORDER,
            fg_color=Colors.SURFACE_LIGHT,
            text_color=Colors.WHITE,
            placeholder_text_color=Colors.GRAY_DIM,
            font=ctk.CTkFont(size=14)
        )
        self.url_entry.pack(fill="x", padx=20, pady=(0, 12))

        # Buttons
        btn_row = ctk.CTkFrame(url_section, fg_color="transparent")
        btn_row.pack(fill="x", padx=20, pady=(0, 18))

        ctk.CTkButton(
            btn_row,
            text="PASTE",
            command=self._paste_url,
            width=100, height=38,
            corner_radius=6,
            fg_color=Colors.FIRE,
            hover_color=Colors.FIRE_GLOW,
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            btn_row,
            text="CLEAR",
            command=lambda: self.url_var.set(""),
            width=80, height=38,
            corner_radius=6,
            fg_color=Colors.SURFACE_LIGHT,
            hover_color=Colors.BORDER,
            border_width=1,
            border_color=Colors.BORDER,
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(side="left")

        # ═══════════════════════════════════════════════════════════════════
        # OUTPUT FOLDER
        # ═══════════════════════════════════════════════════════════════════
        folder_section = ctk.CTkFrame(main, fg_color=Colors.SURFACE, corner_radius=12)
        folder_section.pack(fill="x", pady=(0, 20))

        label_row2 = ctk.CTkFrame(folder_section, fg_color="transparent")
        label_row2.pack(fill="x", padx=20, pady=(18, 12))

        ctk.CTkFrame(label_row2, fg_color=Colors.FIRE, width=4, height=16, corner_radius=0).pack(side="left")
        ctk.CTkLabel(
            label_row2,
            text="SAVE TO",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=Colors.GRAY
        ).pack(side="left", padx=(12, 0))

        folder_row = ctk.CTkFrame(folder_section, fg_color="transparent")
        folder_row.pack(fill="x", padx=20, pady=(0, 18))

        self.folder_entry = ctk.CTkEntry(
            folder_row,
            textvariable=self.output_dir,
            height=44,
            corner_radius=8,
            fg_color=Colors.SURFACE_LIGHT,
            border_color=Colors.BORDER,
            text_color="#cccccc",
            font=ctk.CTkFont(size=12)
        )
        self.folder_entry.pack(side="left", fill="x", expand=True, padx=(0, 12))

        ctk.CTkButton(
            folder_row,
            text="Browse",
            command=self._browse_folder,
            width=85, height=44,
            corner_radius=8,
            fg_color=Colors.SURFACE_LIGHT,
            hover_color=Colors.BORDER,
            border_width=1,
            border_color=Colors.BORDER
        ).pack(side="right")

        # ═══════════════════════════════════════════════════════════════════
        # OPTIONS
        # ═══════════════════════════════════════════════════════════════════
        options_section = ctk.CTkFrame(main, fg_color=Colors.SURFACE, corner_radius=12)
        options_section.pack(fill="x", pady=(0, 25))

        options_inner = ctk.CTkFrame(options_section, fg_color="transparent")
        options_inner.pack(fill="x", padx=20, pady=18)

        # Type
        type_frame = ctk.CTkFrame(options_inner, fg_color="transparent")
        type_frame.pack(side="left", padx=(0, 35))
        ctk.CTkLabel(type_frame, text="TYPE", font=ctk.CTkFont(size=10, weight="bold"),
                    text_color=Colors.GRAY_DIM).pack(anchor="w")
        ctk.CTkSegmentedButton(
            type_frame,
            values=["Video", "Audio"],
            variable=self.media_type,
            command=self._on_type_change,
            font=ctk.CTkFont(size=12)
        ).pack(pady=(6, 0))

        # Format
        format_frame = ctk.CTkFrame(options_inner, fg_color="transparent")
        format_frame.pack(side="left", padx=(0, 35))
        ctk.CTkLabel(format_frame, text="FORMAT", font=ctk.CTkFont(size=10, weight="bold"),
                    text_color=Colors.GRAY_DIM).pack(anchor="w")
        self.format_menu = ctk.CTkOptionMenu(
            format_frame, values=self.video_formats, variable=self.format_var,
            width=100, fg_color=Colors.SURFACE_LIGHT, button_color=Colors.BORDER
        )
        self.format_menu.pack(pady=(6, 0))

        # Quality
        quality_frame = ctk.CTkFrame(options_inner, fg_color="transparent")
        quality_frame.pack(side="left")
        ctk.CTkLabel(quality_frame, text="QUALITY", font=ctk.CTkFont(size=10, weight="bold"),
                    text_color=Colors.GRAY_DIM).pack(anchor="w")
        self.quality_menu = ctk.CTkOptionMenu(
            quality_frame, values=self.video_qualities, variable=self.quality_var,
            width=100, fg_color=Colors.SURFACE_LIGHT, button_color=Colors.BORDER
        )
        self.quality_menu.pack(pady=(6, 0))

        # ═══════════════════════════════════════════════════════════════════
        # DOWNLOAD BUTTON - With glow animation
        # ═══════════════════════════════════════════════════════════════════
        self.download_btn = ctk.CTkButton(
            main,
            text="DOWNLOAD",
            command=self._start_download,
            height=58,
            corner_radius=10,
            fg_color=Colors.FIRE,
            hover_color=Colors.FIRE_GLOW,
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.download_btn.pack(fill="x", pady=(0, 25))

        # ═══════════════════════════════════════════════════════════════════
        # PROGRESS
        # ═══════════════════════════════════════════════════════════════════
        progress_section = ctk.CTkFrame(main, fg_color=Colors.SURFACE, corner_radius=12)
        progress_section.pack(fill="x", pady=(0, 20))

        self.progress_bar = ctk.CTkProgressBar(
            progress_section, height=6, corner_radius=3,
            fg_color=Colors.SURFACE_LIGHT, progress_color=Colors.FIRE
        )
        self.progress_bar.pack(fill="x", padx=20, pady=(18, 10))
        self.progress_bar.set(0)

        self.status_label = ctk.CTkLabel(
            progress_section, text="Ready", font=ctk.CTkFont(size=12),
            text_color=Colors.GRAY_DIM
        )
        self.status_label.pack(pady=(0, 18))

        # ═══════════════════════════════════════════════════════════════════
        # LOG
        # ═══════════════════════════════════════════════════════════════════
        log_section = ctk.CTkFrame(main, fg_color=Colors.SURFACE, corner_radius=12)
        log_section.pack(fill="both", expand=True)

        log_header = ctk.CTkFrame(log_section, fg_color="transparent")
        log_header.pack(fill="x", padx=20, pady=(15, 8))

        ctk.CTkLabel(log_header, text="OUTPUT LOG", font=ctk.CTkFont(size=10, weight="bold"),
                    text_color=Colors.GRAY_DIM).pack(side="left")

        ctk.CTkButton(
            log_header, text="Clear", command=lambda: self.log_text.delete("1.0", "end"),
            width=55, height=26, corner_radius=4,
            fg_color=Colors.SURFACE_LIGHT, hover_color=Colors.BORDER,
            font=ctk.CTkFont(size=10)
        ).pack(side="right")

        self.log_text = ctk.CTkTextbox(
            log_section, height=120, corner_radius=8,
            fg_color=Colors.BLACK, text_color=Colors.GRAY,
            font=ctk.CTkFont(family="Consolas", size=11)
        )
        self.log_text.pack(fill="both", expand=True, padx=20, pady=(0, 18))

        self._log("Flare Download ready. Paste a URL to begin.")

    def _start_glow_animation(self):
        """Subtle pulsing glow on download button."""
        if not self.winfo_exists():
            return

        if not self.is_downloading:
            self._glow_phase += 0.05
            # Subtle brightness variation
            brightness = 0.92 + 0.08 * math.sin(self._glow_phase)
            r = int(0xff * brightness)
            g = int(0x45 * brightness)
            color = f"#{r:02x}{g:02x}00"
            try:
                self.download_btn.configure(fg_color=color)
            except:
                pass

        self.after(80, self._start_glow_animation)

    def _paste_url(self):
        """Simple paste from clipboard."""
        try:
            text = self.clipboard_get()
            if text:
                self.url_var.set(text.strip())
                self._log("URL pasted")
                return
        except:
            pass

        if sys.platform == 'win32':
            try:
                result = subprocess.run(
                    ['powershell', '-command', 'Get-Clipboard'],
                    capture_output=True, text=True, timeout=3,
                    creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0)
                )
                if result.returncode == 0 and result.stdout.strip():
                    self.url_var.set(result.stdout.strip())
                    self._log("URL pasted")
                    return
            except:
                pass

        self._log("Could not read clipboard - try Ctrl+V in the URL box")

    def _browse_folder(self):
        folder = filedialog.askdirectory(initialdir=self.output_dir.get())
        if folder:
            self.output_dir.set(folder)

    def _on_type_change(self, value):
        if value == "Audio":
            self.format_menu.configure(values=self.audio_formats)
            self.format_var.set("mp3")
            self.quality_menu.configure(values=self.audio_qualities)
            self.quality_var.set("Best")
        else:
            self.format_menu.configure(values=self.video_formats)
            self.format_var.set("mp4")
            self.quality_menu.configure(values=self.video_qualities)
            self.quality_var.set("Best")

    def _log(self, message, error=False):
        prefix = "[!] " if error else ""
        self.log_text.insert("end", f"{prefix}{message}\n")
        self.log_text.see("end")

    def _start_download(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning("No URL", "Please enter a video URL")
            return

        if self.is_downloading:
            self._cancel_download()
            return

        self.is_downloading = True
        self.download_btn.configure(text="CANCEL", fg_color="#cc0000", hover_color="#aa0000")
        self.progress_bar.set(0)
        self.status_label.configure(text="Starting download...")

        threading.Thread(target=self._download_thread, args=(url,), daemon=True).start()

    def _cancel_download(self):
        self.is_downloading = False
        self.download_btn.configure(text="DOWNLOAD", fg_color=Colors.FIRE, hover_color=Colors.FIRE_GLOW)
        self.status_label.configure(text="Cancelled")
        self._log("Download cancelled")

    def _progress_hook(self, d):
        """yt-dlp progress callback."""
        if not self.is_downloading:
            raise yt_dlp.utils.DownloadCancelled("Cancelled by user")

        if d['status'] == 'downloading':
            # Get percentage
            if 'total_bytes' in d and d['total_bytes']:
                pct = (d.get('downloaded_bytes', 0) / d['total_bytes']) * 100
            elif 'total_bytes_estimate' in d and d['total_bytes_estimate']:
                pct = (d.get('downloaded_bytes', 0) / d['total_bytes_estimate']) * 100
            elif '_percent_str' in d:
                try:
                    pct = float(d['_percent_str'].replace('%', '').strip())
                except:
                    pct = 0
            else:
                pct = 0

            # Update UI
            self.after(0, lambda p=pct: self.progress_bar.set(p / 100))

            # Status text
            speed = d.get('_speed_str', '')
            eta = d.get('_eta_str', '')
            status = f"Downloading: {pct:.1f}%"
            if speed:
                status += f" • {speed}"
            if eta:
                status += f" • ETA: {eta}"
            self.after(0, lambda s=status: self.status_label.configure(text=s[:55]))

        elif d['status'] == 'finished':
            self.after(0, lambda: self.status_label.configure(text="Processing..."))
            self.after(0, lambda: self._log("Download finished, processing..."))

    def _download_thread(self, url):
        output_dir = self.output_dir.get()
        fmt = self.format_var.get()
        quality = self.quality_var.get()
        is_audio = self.media_type.get() == "Audio"

        self._log(f"Starting download: {url[:70]}...")

        # Build yt-dlp options
        ydl_opts = {
            'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
            'noplaylist': True,
            'socket_timeout': 30,
            'retries': 5,
            'fragment_retries': 5,
            'progress_hooks': [self._progress_hook],
            'quiet': True,
            'no_warnings': True,
        }

        if is_audio:
            # Audio extraction
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': fmt,
            }]
            # Quality mapping (0=best, 9=worst)
            quality_map = {'Best': 0, '320k': 0, '256k': 2, '192k': 4, '128k': 6}
            ydl_opts['postprocessor_args'] = {
                'extractaudio': ['-q:a', str(quality_map.get(quality, 5))]
            }
        else:
            # Video format selection - simple and reliable
            if quality == "Best":
                ydl_opts['format'] = 'bestvideo+bestaudio/best'
            else:
                height = quality.replace("p", "")
                # Try specific height, fallback to best
                ydl_opts['format'] = f'bestvideo[height<={height}]+bestaudio/best[height<={height}]/bestvideo+bestaudio/best'

            # Output format
            if fmt in ['mp4', 'mkv', 'webm']:
                ydl_opts['merge_output_format'] = fmt
            elif fmt in ['mov', 'avi']:
                ydl_opts['merge_output_format'] = 'mp4'
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': fmt,
                }]

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                self.after(0, lambda: self._log("Fetching video info..."))
                info = ydl.extract_info(url, download=True)
                title = info.get('title', 'Unknown')
                self.after(0, lambda t=title: self._log(f"Downloaded: {t}"))

            self.after(0, lambda: self._download_complete(True))

        except yt_dlp.utils.DownloadCancelled:
            self.after(0, lambda: self._log("Download cancelled"))
        except yt_dlp.utils.DownloadError as e:
            error_msg = str(e)
            # Clean up error message
            if "Video unavailable" in error_msg:
                error_msg = "Video unavailable or private"
            elif "Sign in" in error_msg:
                error_msg = "Video requires sign-in (age-restricted or private)"
            elif "HTTP Error 403" in error_msg:
                error_msg = "Access forbidden - video may be region-locked"
            elif "HTTP Error 404" in error_msg:
                error_msg = "Video not found"
            else:
                error_msg = error_msg[:100]
            self.after(0, lambda e=error_msg: self._download_complete(False, e))
        except Exception as e:
            self.after(0, lambda e=str(e)[:100]: self._download_complete(False, e))

    def _download_complete(self, success, error=None):
        self.is_downloading = False
        self.download_btn.configure(text="DOWNLOAD", fg_color=Colors.FIRE, hover_color=Colors.FIRE_GLOW)

        if success:
            self.progress_bar.set(1)
            self.status_label.configure(text="Download complete!")
            self._log("Download complete!")
            messagebox.showinfo("Success", "Download complete!")
        else:
            self.status_label.configure(text="Failed")
            self._log(f"Error: {error}", error=True)

    def _on_close(self):
        self.is_downloading = False
        self.destroy()


def main():
    try:
        app = FlareDownloadApp()
        app.mainloop()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
