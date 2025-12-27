#!/usr/bin/env python3
"""
FLARE DOWNLOAD
Premium Multi-Platform Video Downloader
Part of the Flare ecosystem
Design: Minimal. Bold. Cinematic.
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import os
import re
import subprocess
from datetime import datetime
from typing import Optional

try:
    from version import __version__
except ImportError:
    __version__ = "2.5.0"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


# =============================================================================
# FLARE DESIGN TOKENS
# Minimal. Bold. Cinematic.
# =============================================================================
class F:
    """Design tokens matching flare.mukundthiru.com"""
    # Pure black
    BLACK = "#000000"

    # Surfaces
    SURFACE = "#0a0a0a"
    SURFACE_2 = "#111111"

    # Borders
    BORDER = "#1a1a1a"
    BORDER_HOVER = "#2a2a2a"

    # Fire orange - THE accent
    FIRE = "#ff6b35"
    FIRE_HOVER = "#ff8c00"

    # Text
    WHITE = "#ffffff"
    GRAY = "#666666"
    GRAY_DARK = "#444444"

    # Status
    SUCCESS = "#22c55e"
    ERROR = "#ef4444"


class FlareApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("FLARE DOWNLOAD")
        self.geometry("860x900")
        self.minsize(760, 800)
        self.configure(fg_color=F.BLACK)

        self.is_downloading = False
        self.process: Optional[subprocess.Popen] = None

        self.url_var = ctk.StringVar()
        self.output_dir = ctk.StringVar(value=os.path.expanduser("~/Downloads"))
        self.format_var = ctk.StringVar(value="mp4")
        self.quality_var = ctk.StringVar(value="Best")
        self.media_type = ctk.StringVar(value="Video")

        self.video_formats = ["mp4", "webm", "mkv"]
        self.audio_formats = ["mp3", "m4a", "wav", "flac"]
        self.video_qualities = ["Best", "4K", "1080p", "720p", "480p"]
        self.audio_qualities = ["Best", "320k", "256k", "192k", "128k"]

        self._build()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build(self):
        # Container
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=40, pady=40)

        self._header(container)
        self._content(container)
        self._footer(container)

    def _header(self, parent):
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(fill="x", pady=(0, 40))

        # FLARE title - large, bold
        title = ctk.CTkLabel(
            header,
            text="FLARE",
            font=ctk.CTkFont(size=42, weight="bold"),
            text_color=F.WHITE
        )
        title.pack(side="left")

        # Orange square accent
        ctk.CTkFrame(header, fg_color=F.FIRE, width=6, height=6, corner_radius=0).pack(
            side="left", padx=(10, 10), pady=(12, 0)
        )

        # DOWNLOAD subtitle
        subtitle = ctk.CTkLabel(
            header,
            text="DOWNLOAD",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=F.GRAY
        )
        subtitle.pack(side="left", pady=(14, 0))

        # Version
        ctk.CTkLabel(
            header,
            text=f"v{__version__}",
            font=ctk.CTkFont(family="Consolas", size=9),
            text_color=F.GRAY_DARK
        ).pack(side="right", pady=(14, 0))

    def _content(self, parent):
        content = ctk.CTkFrame(parent, fg_color="transparent")
        content.pack(fill="both", expand=True)

        self._url_section(content)
        self._options_section(content)
        self._output_section(content)
        self._action_section(content)
        self._progress_section(content)
        self._log_section(content)

    def _url_section(self, parent):
        section = ctk.CTkFrame(parent, fg_color="transparent")
        section.pack(fill="x", pady=(0, 28))

        # Label with tracking
        ctk.CTkLabel(
            section,
            text="VIDEO URL",
            font=ctk.CTkFont(size=9, weight="bold"),
            text_color=F.GRAY
        ).pack(anchor="w", pady=(0, 10))

        # Input with corner accents
        input_frame = ctk.CTkFrame(section, fg_color="transparent")
        input_frame.pack(fill="x")

        # Corner decorations
        corner_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        corner_frame.pack(fill="x")

        # Entry
        self.url_entry = ctk.CTkEntry(
            corner_frame,
            textvariable=self.url_var,
            placeholder_text="https://...",
            height=52,
            corner_radius=0,
            border_width=1,
            border_color=F.BORDER,
            fg_color=F.SURFACE,
            text_color=F.WHITE,
            placeholder_text_color=F.GRAY_DARK,
            font=ctk.CTkFont(size=13)
        )
        self.url_entry.pack(fill="x")
        self.url_entry.bind("<FocusIn>", lambda e: self.url_entry.configure(border_color=F.FIRE))
        self.url_entry.bind("<FocusOut>", lambda e: self.url_entry.configure(border_color=F.BORDER))

        # Corner accents (top-left, top-right, bottom-left, bottom-right)
        corners = ctk.CTkFrame(corner_frame, fg_color="transparent")
        corners.place(relwidth=1, relheight=1)

        # TL
        ctk.CTkFrame(corners, fg_color=F.FIRE, width=12, height=2, corner_radius=0).place(x=0, y=0)
        ctk.CTkFrame(corners, fg_color=F.FIRE, width=2, height=12, corner_radius=0).place(x=0, y=0)
        # TR
        ctk.CTkFrame(corners, fg_color=F.FIRE, width=12, height=2, corner_radius=0).place(relx=1, x=-12, y=0)
        ctk.CTkFrame(corners, fg_color=F.FIRE, width=2, height=12, corner_radius=0).place(relx=1, x=-2, y=0)
        # BL
        ctk.CTkFrame(corners, fg_color=F.FIRE, width=12, height=2, corner_radius=0).place(x=0, rely=1, y=-2)
        ctk.CTkFrame(corners, fg_color=F.FIRE, width=2, height=12, corner_radius=0).place(x=0, rely=1, y=-12)
        # BR
        ctk.CTkFrame(corners, fg_color=F.FIRE, width=12, height=2, corner_radius=0).place(relx=1, x=-12, rely=1, y=-2)
        ctk.CTkFrame(corners, fg_color=F.FIRE, width=2, height=12, corner_radius=0).place(relx=1, x=-2, rely=1, y=-12)

        # Buttons
        btns = ctk.CTkFrame(section, fg_color="transparent")
        btns.pack(fill="x", pady=(12, 0))

        for text, cmd in [("PASTE", self._paste), ("CLEAR", self._clear)]:
            ctk.CTkButton(
                btns, text=text, command=cmd,
                width=70, height=28, corner_radius=0,
                fg_color="transparent", hover_color=F.SURFACE,
                border_width=1, border_color=F.BORDER,
                text_color=F.GRAY, font=ctk.CTkFont(size=9, weight="bold")
            ).pack(side="left", padx=(0, 6))

        ctk.CTkLabel(
            btns,
            text="YouTube • TikTok • Instagram • Twitter • 1000+",
            font=ctk.CTkFont(size=8),
            text_color=F.GRAY_DARK
        ).pack(side="right")

    def _options_section(self, parent):
        section = ctk.CTkFrame(parent, fg_color="transparent")
        section.pack(fill="x", pady=(0, 28))
        section.columnconfigure((0, 1, 2), weight=1, uniform="col")

        # Type
        type_f = ctk.CTkFrame(section, fg_color="transparent")
        type_f.grid(row=0, column=0, sticky="ew", padx=(0, 12))
        ctk.CTkLabel(type_f, text="TYPE", font=ctk.CTkFont(size=9, weight="bold"), text_color=F.GRAY).pack(anchor="w", pady=(0, 6))
        self.type_seg = ctk.CTkSegmentedButton(
            type_f, values=["Video", "Audio"], variable=self.media_type,
            command=self._on_type_change, height=38, corner_radius=0,
            font=ctk.CTkFont(size=10, weight="bold"),
            fg_color=F.SURFACE, selected_color=F.FIRE, selected_hover_color=F.FIRE_HOVER,
            unselected_color=F.SURFACE, unselected_hover_color=F.SURFACE_2,
            text_color=F.WHITE
        )
        self.type_seg.pack(fill="x")

        # Format
        fmt_f = ctk.CTkFrame(section, fg_color="transparent")
        fmt_f.grid(row=0, column=1, sticky="ew", padx=6)
        ctk.CTkLabel(fmt_f, text="FORMAT", font=ctk.CTkFont(size=9, weight="bold"), text_color=F.GRAY).pack(anchor="w", pady=(0, 6))
        self.fmt_menu = ctk.CTkOptionMenu(
            fmt_f, values=self.video_formats, variable=self.format_var,
            height=38, corner_radius=0, fg_color=F.SURFACE,
            button_color=F.SURFACE_2, button_hover_color=F.BORDER_HOVER,
            dropdown_fg_color=F.SURFACE, dropdown_hover_color=F.FIRE,
            text_color=F.WHITE, font=ctk.CTkFont(size=11)
        )
        self.fmt_menu.pack(fill="x")

        # Quality
        qual_f = ctk.CTkFrame(section, fg_color="transparent")
        qual_f.grid(row=0, column=2, sticky="ew", padx=(12, 0))
        ctk.CTkLabel(qual_f, text="QUALITY", font=ctk.CTkFont(size=9, weight="bold"), text_color=F.GRAY).pack(anchor="w", pady=(0, 6))
        self.qual_menu = ctk.CTkOptionMenu(
            qual_f, values=self.video_qualities, variable=self.quality_var,
            height=38, corner_radius=0, fg_color=F.SURFACE,
            button_color=F.SURFACE_2, button_hover_color=F.BORDER_HOVER,
            dropdown_fg_color=F.SURFACE, dropdown_hover_color=F.FIRE,
            text_color=F.WHITE, font=ctk.CTkFont(size=11)
        )
        self.qual_menu.pack(fill="x")

    def _output_section(self, parent):
        section = ctk.CTkFrame(parent, fg_color="transparent")
        section.pack(fill="x", pady=(0, 28))

        ctk.CTkLabel(section, text="SAVE TO", font=ctk.CTkFont(size=9, weight="bold"), text_color=F.GRAY).pack(anchor="w", pady=(0, 6))

        row = ctk.CTkFrame(section, fg_color="transparent")
        row.pack(fill="x")

        self.path_entry = ctk.CTkEntry(
            row, textvariable=self.output_dir, height=38, corner_radius=0,
            border_width=1, border_color=F.BORDER, fg_color=F.SURFACE,
            text_color=F.WHITE, font=ctk.CTkFont(size=11)
        )
        self.path_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        ctk.CTkButton(
            row, text="BROWSE", command=self._browse,
            width=80, height=38, corner_radius=0,
            fg_color="transparent", hover_color=F.SURFACE,
            border_width=1, border_color=F.BORDER,
            text_color=F.GRAY, font=ctk.CTkFont(size=9, weight="bold")
        ).pack(side="right")

    def _action_section(self, parent):
        section = ctk.CTkFrame(parent, fg_color="transparent")
        section.pack(fill="x", pady=(0, 28))

        row = ctk.CTkFrame(section, fg_color="transparent")
        row.pack(fill="x")

        # Download - PRIMARY ACTION
        self.dl_btn = ctk.CTkButton(
            row, text="DOWNLOAD", command=self._download,
            height=52, corner_radius=0,
            fg_color=F.FIRE, hover_color=F.FIRE_HOVER,
            text_color=F.BLACK, font=ctk.CTkFont(size=13, weight="bold")
        )
        self.dl_btn.pack(side="left", fill="x", expand=True, padx=(0, 10))

        # Cancel
        self.cancel_btn = ctk.CTkButton(
            row, text="CANCEL", command=self._cancel,
            width=90, height=52, corner_radius=0,
            fg_color=F.SURFACE, hover_color=F.ERROR,
            text_color=F.GRAY, state="disabled",
            font=ctk.CTkFont(size=10, weight="bold")
        )
        self.cancel_btn.pack(side="right")

    def _progress_section(self, parent):
        section = ctk.CTkFrame(parent, fg_color=F.SURFACE, corner_radius=0)
        section.pack(fill="x", pady=(0, 20))

        inner = ctk.CTkFrame(section, fg_color="transparent")
        inner.pack(fill="x", padx=20, pady=16)

        # Status
        status_row = ctk.CTkFrame(inner, fg_color="transparent")
        status_row.pack(fill="x", pady=(0, 10))

        self.status_lbl = ctk.CTkLabel(status_row, text="Ready", font=ctk.CTkFont(size=10), text_color=F.GRAY)
        self.status_lbl.pack(side="left")

        self.speed_lbl = ctk.CTkLabel(status_row, text="", font=ctk.CTkFont(family="Consolas", size=10), text_color=F.FIRE)
        self.speed_lbl.pack(side="right")

        # Progress bar - thin
        self.progress = ctk.CTkProgressBar(inner, height=3, corner_radius=0, progress_color=F.FIRE, fg_color=F.BORDER)
        self.progress.pack(fill="x")
        self.progress.set(0)

        # Percent
        self.pct_lbl = ctk.CTkLabel(inner, text="0%", font=ctk.CTkFont(family="Consolas", size=9), text_color=F.GRAY_DARK)
        self.pct_lbl.pack(anchor="e", pady=(6, 0))

    def _log_section(self, parent):
        section = ctk.CTkFrame(parent, fg_color="transparent")
        section.pack(fill="both", expand=True)

        header = ctk.CTkFrame(section, fg_color="transparent")
        header.pack(fill="x", pady=(0, 6))

        ctk.CTkLabel(header, text="LOG", font=ctk.CTkFont(size=9, weight="bold"), text_color=F.GRAY_DARK).pack(side="left")
        ctk.CTkButton(
            header, text="CLEAR", command=self._clear_log,
            width=50, height=20, corner_radius=0,
            fg_color="transparent", hover_color=F.SURFACE,
            text_color=F.GRAY_DARK, font=ctk.CTkFont(size=8)
        ).pack(side="right")

        self.log = ctk.CTkTextbox(
            section, height=100, corner_radius=0,
            fg_color=F.SURFACE, text_color=F.GRAY,
            font=ctk.CTkFont(family="Consolas", size=9),
            border_width=1, border_color=F.BORDER
        )
        self.log.pack(fill="both", expand=True)

    def _footer(self, parent):
        footer = ctk.CTkFrame(parent, fg_color="transparent")
        footer.pack(fill="x", pady=(20, 0))

        # Orange line
        ctk.CTkFrame(footer, fg_color=F.FIRE, height=1, corner_radius=0).pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            footer,
            text="FLARE ECOSYSTEM  •  YT-DLP",
            font=ctk.CTkFont(size=8),
            text_color=F.GRAY_DARK
        ).pack()

    # =========================================================================
    # HANDLERS
    # =========================================================================
    def _paste(self):
        try:
            self.url_var.set(self.clipboard_get())
            self._log_msg("URL pasted")
        except: pass

    def _clear(self):
        self.url_var.set("")

    def _clear_log(self):
        self.log.delete("1.0", "end")

    def _browse(self):
        folder = filedialog.askdirectory(initialdir=self.output_dir.get())
        if folder:
            self.output_dir.set(folder)

    def _on_type_change(self, val):
        if val == "Audio":
            self.fmt_menu.configure(values=self.audio_formats)
            self.format_var.set("mp3")
            self.qual_menu.configure(values=self.audio_qualities)
            self.quality_var.set("Best")
        else:
            self.fmt_menu.configure(values=self.video_formats)
            self.format_var.set("mp4")
            self.qual_menu.configure(values=self.video_qualities)
            self.quality_var.set("Best")

    def _log_msg(self, msg, ok=True):
        ts = datetime.now().strftime("%H:%M:%S")
        icon = "✓" if ok else "✗"
        self.log.insert("end", f"{ts}  {icon}  {msg}\n")
        self.log.see("end")

    def _update_progress(self, pct, status="", speed=""):
        self.progress.set(pct / 100)
        self.pct_lbl.configure(text=f"{pct:.0f}%")
        if status: self.status_lbl.configure(text=status)
        self.speed_lbl.configure(text=speed)

    def _set_downloading(self, state):
        self.is_downloading = state
        if state:
            self.dl_btn.configure(state="disabled", fg_color=F.GRAY_DARK, text="DOWNLOADING...")
            self.cancel_btn.configure(state="normal", text_color=F.WHITE)
        else:
            self.dl_btn.configure(state="normal", fg_color=F.FIRE, text="DOWNLOAD")
            self.cancel_btn.configure(state="disabled", text_color=F.GRAY)

    # =========================================================================
    # DOWNLOAD
    # =========================================================================
    def _download(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("Error", "Enter a URL")
            return
        if not re.match(r'^https?://', url):
            messagebox.showerror("Error", "Invalid URL")
            return
        if not os.path.isdir(self.output_dir.get()):
            messagebox.showerror("Error", "Folder doesn't exist")
            return

        self._set_downloading(True)
        self._update_progress(0, "Starting...")
        self._log_msg(f"Downloading: {url[:50]}...")

        threading.Thread(target=self._dl_thread, args=(url,), daemon=True).start()

    def _cancel(self):
        if self.process:
            self.process.terminate()
            self._log_msg("Cancelled", False)
            self._finish(False)

    def _dl_thread(self, url):
        try:
            out_dir = self.output_dir.get()
            fmt = self.format_var.get()
            quality = self.quality_var.get()
            is_audio = self.media_type.get() == "Audio"

            template = os.path.join(out_dir, "%(title)s.%(ext)s")

            # Find yt-dlp
            if os.name == 'nt':
                base = os.path.dirname(os.path.abspath(__file__))
                bundled = os.path.join(base, "python", "Scripts", "yt-dlp.exe")
                ytdlp = bundled if os.path.exists(bundled) else "yt-dlp"
            else:
                ytdlp = "yt-dlp"

            cmd = [ytdlp, "--newline", "--progress", "--no-warnings", "--no-playlist", "--restrict-filenames"]

            if is_audio:
                cmd.extend(["-x", "--audio-format", fmt])
                if quality != "Best":
                    br = quality.replace("k", "")
                    cmd.extend(["--audio-quality", f"{br}K"])
            else:
                if quality == "Best":
                    cmd.extend(["-f", "bestvideo+bestaudio/best"])
                elif quality == "4K":
                    cmd.extend(["-f", "bestvideo[height<=2160]+bestaudio/best"])
                else:
                    h = quality.replace("p", "")
                    cmd.extend(["-f", f"bestvideo[height<={h}]+bestaudio/best"])
                cmd.extend(["--merge-output-format", fmt])

            cmd.extend(["-o", template, url])

            # Env with bundled tools
            env = os.environ.copy()
            if os.name == 'nt':
                base = os.path.dirname(os.path.abspath(__file__))
                paths = [
                    os.path.join(base, "python"),
                    os.path.join(base, "python", "Scripts"),
                    os.path.join(base, "ffmpeg"),
                    os.path.join(base, "node"),
                ]
                env["PATH"] = ";".join(paths) + ";" + env.get("PATH", "")

            self.process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                universal_newlines=True, bufsize=1, env=env,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )

            for line in self.process.stdout:
                line = line.strip()
                if not line: continue

                m = re.search(r'(\d+\.?\d*)%', line)
                s = re.search(r'at\s+([\d.]+\s*\w+/s)', line)

                if m:
                    pct = float(m.group(1))
                    spd = s.group(1) if s else ""
                    self.after(0, lambda p=pct, sp=spd: self._update_progress(p, "Downloading...", sp))

            self.process.wait()
            self.after(0, lambda: self._finish(self.process.returncode == 0))

        except FileNotFoundError:
            self.after(0, lambda: self._finish(False, "yt-dlp not found"))
        except Exception as e:
            self.after(0, lambda: self._finish(False, str(e)[:40]))
        finally:
            self.process = None

    def _finish(self, success, error=None):
        self._set_downloading(False)
        if success:
            self._update_progress(100, "Complete", "")
            self._log_msg("Download complete")
            self.progress.configure(progress_color=F.SUCCESS)
        else:
            self._update_progress(0, "Failed", "")
            self._log_msg(error or "Failed", False)
            self.progress.configure(progress_color=F.ERROR)
        self.after(2000, lambda: self.progress.configure(progress_color=F.FIRE))

    def _on_close(self):
        if self.is_downloading:
            if messagebox.askyesno("Confirm", "Cancel and exit?"):
                if self.process: self.process.terminate()
                self.destroy()
        else:
            self.destroy()


def main():
    app = FlareApp()
    app.mainloop()


if __name__ == "__main__":
    main()
