#!/usr/bin/env python3
"""
NeonTube - A Futuristic Multi-Platform Video Downloader
Supports YouTube, TikTok, Instagram, Twitter, and 1000+ sites
Version 2.2 - Multi-Platform Edition
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import os
import re
import subprocess
import json
from datetime import datetime
from typing import Optional

# Version info
try:
    from version import __version__
except ImportError:
    __version__ = "2.2.0"

# Set appearance mode and default color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class GlowingFrame(ctk.CTkFrame):
    """Custom frame with glowing border effect"""
    def __init__(self, master, glow_color="#00d4ff", **kwargs):
        super().__init__(master, **kwargs)
        self.configure(
            corner_radius=15,
            border_width=2,
            border_color=glow_color
        )


class YouTubeDownloader(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window configuration
        self.title(f"NeonTube v{__version__} - Video Downloader")
        self.geometry("950x850")
        self.minsize(900, 800)

        # Supported platforms
        self.supported_platforms = [
            "YouTube", "TikTok", "Instagram", "Twitter/X", "Facebook",
            "Vimeo", "Dailymotion", "Twitch", "Reddit", "SoundCloud",
            "Spotify", "Bandcamp", "Bilibili", "Pinterest", "Tumblr"
        ]

        # Colors for futuristic theme
        self.colors = {
            "bg_dark": "#0a0a0f",
            "bg_medium": "#12121a",
            "bg_light": "#1a1a25",
            "accent_cyan": "#00d4ff",
            "accent_purple": "#9945ff",
            "accent_pink": "#ff00aa",
            "accent_green": "#00ff88",
            "text_primary": "#ffffff",
            "text_secondary": "#8888aa",
            "success": "#00ff88",
            "warning": "#ffaa00",
            "error": "#ff4455"
        }

        self.configure(fg_color=self.colors["bg_dark"])

        # Variables
        self.download_path = ctk.StringVar(value=os.path.expanduser("~/Downloads"))
        self.format_var = ctk.StringVar(value="mp4")
        self.quality_var = ctk.StringVar(value="Best Quality")
        self.audio_quality_var = ctk.StringVar(value="320 kbps")
        self.type_var = ctk.StringVar(value="Video")
        self.is_downloading = False
        self.current_process: Optional[subprocess.Popen] = None

        # Options variables
        self.download_subtitles = ctk.BooleanVar(value=False)
        self.download_thumbnail = ctk.BooleanVar(value=False)
        self.embed_metadata = ctk.BooleanVar(value=True)
        self.prefer_ffmpeg = ctk.BooleanVar(value=True)

        # Quality options
        self.video_qualities = [
            "Best Quality", "8K (4320p)", "4K (2160p)", "2K (1440p)", "1080p (Full HD)",
            "720p (HD)", "480p (SD)", "360p", "240p", "144p"
        ]
        self.audio_qualities = [
            "320 kbps (Best)", "256 kbps", "192 kbps", "128 kbps", "96 kbps", "64 kbps"
        ]

        # Format categories
        self.video_formats = ["mp4", "webm", "mkv", "avi", "mov"]
        self.audio_formats = ["mp3", "wav", "m4a", "flac", "aac", "opus", "ogg"]

        # Create scrollable main frame
        self.main_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.main_scroll.pack(fill="both", expand=True)

        # Create UI
        self.create_header()
        self.create_main_content()
        self.create_footer()

        # Start animation
        self.animate_glow()

        # Bind window close event
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_header(self):
        """Create the futuristic header"""
        header_frame = ctk.CTkFrame(
            self.main_scroll,
            fg_color=self.colors["bg_medium"],
            corner_radius=0,
            height=90
        )
        header_frame.pack(fill="x", padx=0, pady=0)
        header_frame.pack_propagate(False)

        # Logo and title container
        title_container = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_container.pack(expand=True, fill="both", padx=30, pady=15)

        # Neon title
        self.title_label = ctk.CTkLabel(
            title_container,
            text="NEONTUBE",
            font=ctk.CTkFont(family="Segoe UI", size=32, weight="bold"),
            text_color=self.colors["accent_cyan"]
        )
        self.title_label.pack(side="left")

        # Subtitle
        subtitle = ctk.CTkLabel(
            title_container,
            text="  MULTI-PLATFORM VIDEO DOWNLOADER",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=self.colors["text_secondary"]
        )
        subtitle.pack(side="left", padx=10, pady=(12, 0))

        # Right side buttons
        right_frame = ctk.CTkFrame(title_container, fg_color="transparent")
        right_frame.pack(side="right")

        # Update button
        update_btn = ctk.CTkButton(
            right_frame,
            text="Check Updates",
            command=self.check_for_updates,
            width=100,
            height=28,
            corner_radius=5,
            fg_color="transparent",
            border_width=1,
            border_color=self.colors["accent_green"],
            hover_color=self.colors["bg_light"],
            font=ctk.CTkFont(size=10)
        )
        update_btn.pack(side="left", padx=(0, 8))

        # Version badge
        version_badge = ctk.CTkLabel(
            right_frame,
            text=f"v{__version__}",
            font=ctk.CTkFont(size=10),
            fg_color=self.colors["accent_purple"],
            corner_radius=5,
            padx=8,
            pady=2
        )
        version_badge.pack(side="left")

    def create_main_content(self):
        """Create the main content area"""
        main_frame = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=25, pady=15)

        # URL Input Section
        self.create_url_section(main_frame)

        # Options Section
        self.create_options_section(main_frame)

        # Advanced Options Section
        self.create_advanced_options(main_frame)

        # Download Button
        self.create_download_button(main_frame)

        # Progress Section
        self.create_progress_section(main_frame)

        # Log Section
        self.create_log_section(main_frame)

    def create_url_section(self, parent):
        """Create URL input section"""
        url_frame = GlowingFrame(parent, fg_color=self.colors["bg_medium"])
        url_frame.pack(fill="x", pady=(0, 12))

        # Section title with icon
        title_row = ctk.CTkFrame(url_frame, fg_color="transparent")
        title_row.pack(fill="x", padx=20, pady=(12, 5))

        url_title = ctk.CTkLabel(
            title_row,
            text="VIDEO / PLAYLIST URL",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.colors["accent_cyan"]
        )
        url_title.pack(side="left")

        # Supported platforms label
        platforms_text = " | ".join(self.supported_platforms[:6]) + " + 1000 more"
        platforms_label = ctk.CTkLabel(
            title_row,
            text=platforms_text,
            font=ctk.CTkFont(size=9),
            text_color=self.colors["text_secondary"]
        )
        platforms_label.pack(side="right")

        # URL input with buttons
        input_frame = ctk.CTkFrame(url_frame, fg_color="transparent")
        input_frame.pack(fill="x", padx=20, pady=(0, 12))

        self.url_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Paste any video URL here (YouTube, TikTok, Instagram, Twitter, etc.)...",
            height=45,
            corner_radius=10,
            border_width=1,
            border_color=self.colors["bg_light"],
            fg_color=self.colors["bg_dark"],
            font=ctk.CTkFont(size=13)
        )
        self.url_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        # Button container
        btn_container = ctk.CTkFrame(input_frame, fg_color="transparent")
        btn_container.pack(side="right")

        paste_btn = ctk.CTkButton(
            btn_container,
            text="PASTE",
            command=self.paste_url,
            width=70,
            height=45,
            corner_radius=8,
            fg_color=self.colors["accent_purple"],
            hover_color="#7733cc"
        )
        paste_btn.pack(side="left", padx=(0, 5))

        clear_btn = ctk.CTkButton(
            btn_container,
            text="CLEAR",
            command=self.clear_url,
            width=70,
            height=45,
            corner_radius=8,
            fg_color=self.colors["bg_light"],
            hover_color=self.colors["error"]
        )
        clear_btn.pack(side="left")

        # Video info button
        info_btn = ctk.CTkButton(
            url_frame,
            text="FETCH VIDEO INFO",
            command=self.fetch_video_info,
            fg_color="transparent",
            border_width=1,
            border_color=self.colors["accent_cyan"],
            hover_color=self.colors["bg_light"],
            height=32,
            corner_radius=8,
            font=ctk.CTkFont(size=11)
        )
        info_btn.pack(anchor="e", padx=20, pady=(0, 12))

    def create_options_section(self, parent):
        """Create options section"""
        options_frame = GlowingFrame(parent, fg_color=self.colors["bg_medium"])
        options_frame.pack(fill="x", pady=(0, 12))

        # Section title
        options_title = ctk.CTkLabel(
            options_frame,
            text="DOWNLOAD OPTIONS",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.colors["accent_cyan"]
        )
        options_title.pack(anchor="w", padx=20, pady=(12, 8))

        # Options row 1 - Type, Format, Quality
        opts_row1 = ctk.CTkFrame(options_frame, fg_color="transparent")
        opts_row1.pack(fill="x", padx=20, pady=(0, 10))

        # Type selection (Video/Audio)
        type_frame = ctk.CTkFrame(opts_row1, fg_color="transparent")
        type_frame.pack(side="left", expand=True, fill="x", padx=(0, 8))

        ctk.CTkLabel(
            type_frame,
            text="MEDIA TYPE",
            font=ctk.CTkFont(size=10),
            text_color=self.colors["text_secondary"]
        ).pack(anchor="w")

        self.type_menu = ctk.CTkSegmentedButton(
            type_frame,
            values=["Video", "Audio"],
            variable=self.type_var,
            font=ctk.CTkFont(size=11),
            corner_radius=8,
            selected_color=self.colors["accent_cyan"],
            selected_hover_color="#0099cc",
            command=self.on_type_change,
            height=35
        )
        self.type_menu.pack(fill="x", pady=(4, 0))

        # Format selection
        format_frame = ctk.CTkFrame(opts_row1, fg_color="transparent")
        format_frame.pack(side="left", expand=True, fill="x", padx=8)

        ctk.CTkLabel(
            format_frame,
            text="OUTPUT FORMAT",
            font=ctk.CTkFont(size=10),
            text_color=self.colors["text_secondary"]
        ).pack(anchor="w")

        self.format_menu = ctk.CTkOptionMenu(
            format_frame,
            values=self.video_formats,
            variable=self.format_var,
            font=ctk.CTkFont(size=11),
            corner_radius=8,
            fg_color=self.colors["bg_dark"],
            button_color=self.colors["accent_cyan"],
            button_hover_color="#0099cc",
            dropdown_fg_color=self.colors["bg_medium"],
            dropdown_hover_color=self.colors["accent_cyan"],
            height=35,
            width=120
        )
        self.format_menu.pack(fill="x", pady=(4, 0))

        # Quality selection container
        self.quality_frame = ctk.CTkFrame(opts_row1, fg_color="transparent")
        self.quality_frame.pack(side="left", expand=True, fill="x", padx=(8, 0))

        self.quality_label = ctk.CTkLabel(
            self.quality_frame,
            text="VIDEO QUALITY",
            font=ctk.CTkFont(size=10),
            text_color=self.colors["text_secondary"]
        )
        self.quality_label.pack(anchor="w")

        self.quality_menu = ctk.CTkOptionMenu(
            self.quality_frame,
            values=self.video_qualities,
            variable=self.quality_var,
            font=ctk.CTkFont(size=11),
            corner_radius=8,
            fg_color=self.colors["bg_dark"],
            button_color=self.colors["accent_purple"],
            button_hover_color="#7733cc",
            dropdown_fg_color=self.colors["bg_medium"],
            dropdown_hover_color=self.colors["accent_purple"],
            height=35,
            width=140
        )
        self.quality_menu.pack(fill="x", pady=(4, 0))

        # Audio quality menu (hidden by default)
        self.audio_quality_menu = ctk.CTkOptionMenu(
            self.quality_frame,
            values=self.audio_qualities,
            variable=self.audio_quality_var,
            font=ctk.CTkFont(size=11),
            corner_radius=8,
            fg_color=self.colors["bg_dark"],
            button_color=self.colors["accent_purple"],
            button_hover_color="#7733cc",
            dropdown_fg_color=self.colors["bg_medium"],
            dropdown_hover_color=self.colors["accent_purple"],
            height=35,
            width=140
        )

        # Download path row
        path_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        path_frame.pack(fill="x", padx=20, pady=(0, 12))

        ctk.CTkLabel(
            path_frame,
            text="SAVE LOCATION",
            font=ctk.CTkFont(size=10),
            text_color=self.colors["text_secondary"]
        ).pack(anchor="w")

        path_input_frame = ctk.CTkFrame(path_frame, fg_color="transparent")
        path_input_frame.pack(fill="x", pady=(4, 0))

        self.path_entry = ctk.CTkEntry(
            path_input_frame,
            textvariable=self.download_path,
            height=38,
            corner_radius=8,
            border_width=1,
            border_color=self.colors["bg_light"],
            fg_color=self.colors["bg_dark"],
            font=ctk.CTkFont(size=11)
        )
        self.path_entry.pack(side="left", expand=True, fill="x", padx=(0, 10))

        browse_btn = ctk.CTkButton(
            path_input_frame,
            text="BROWSE",
            command=self.browse_path,
            width=90,
            height=38,
            corner_radius=8,
            fg_color=self.colors["bg_light"],
            hover_color=self.colors["accent_purple"]
        )
        browse_btn.pack(side="right")

    def create_advanced_options(self, parent):
        """Create advanced options section"""
        adv_frame = GlowingFrame(parent, glow_color=self.colors["accent_purple"], fg_color=self.colors["bg_medium"])
        adv_frame.pack(fill="x", pady=(0, 12))

        # Collapsible header
        header_frame = ctk.CTkFrame(adv_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(12, 8))

        adv_title = ctk.CTkLabel(
            header_frame,
            text="ADVANCED OPTIONS",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.colors["accent_purple"]
        )
        adv_title.pack(side="left")

        # Options grid
        opts_grid = ctk.CTkFrame(adv_frame, fg_color="transparent")
        opts_grid.pack(fill="x", padx=20, pady=(0, 12))

        # Row 1
        row1 = ctk.CTkFrame(opts_grid, fg_color="transparent")
        row1.pack(fill="x", pady=(0, 8))

        # Subtitles
        self.subtitles_check = ctk.CTkCheckBox(
            row1,
            text="Download Subtitles (if available)",
            variable=self.download_subtitles,
            font=ctk.CTkFont(size=11),
            fg_color=self.colors["accent_cyan"],
            hover_color="#0099cc",
            corner_radius=4
        )
        self.subtitles_check.pack(side="left", padx=(0, 20))

        # Thumbnail
        self.thumbnail_check = ctk.CTkCheckBox(
            row1,
            text="Download Thumbnail",
            variable=self.download_thumbnail,
            font=ctk.CTkFont(size=11),
            fg_color=self.colors["accent_cyan"],
            hover_color="#0099cc",
            corner_radius=4
        )
        self.thumbnail_check.pack(side="left", padx=(0, 20))

        # Row 2
        row2 = ctk.CTkFrame(opts_grid, fg_color="transparent")
        row2.pack(fill="x")

        # Embed metadata
        self.metadata_check = ctk.CTkCheckBox(
            row2,
            text="Embed Metadata (title, artist, etc.)",
            variable=self.embed_metadata,
            font=ctk.CTkFont(size=11),
            fg_color=self.colors["accent_cyan"],
            hover_color="#0099cc",
            corner_radius=4
        )
        self.metadata_check.pack(side="left", padx=(0, 20))

        # FFmpeg preference
        self.ffmpeg_check = ctk.CTkCheckBox(
            row2,
            text="Use FFmpeg for merging",
            variable=self.prefer_ffmpeg,
            font=ctk.CTkFont(size=11),
            fg_color=self.colors["accent_cyan"],
            hover_color="#0099cc",
            corner_radius=4
        )
        self.ffmpeg_check.pack(side="left")

    def create_download_button(self, parent):
        """Create the main download button and cancel button"""
        btn_frame = ctk.CTkFrame(parent, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(0, 12))

        self.download_btn = ctk.CTkButton(
            btn_frame,
            text="DOWNLOAD",
            command=self.start_download,
            height=55,
            corner_radius=12,
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            fg_color=self.colors["accent_cyan"],
            hover_color="#0099cc",
            border_width=2,
            border_color=self.colors["accent_cyan"]
        )
        self.download_btn.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.cancel_btn = ctk.CTkButton(
            btn_frame,
            text="CANCEL",
            command=self.cancel_download,
            height=55,
            width=100,
            corner_radius=12,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=self.colors["error"],
            hover_color="#cc3344",
            state="disabled"
        )
        self.cancel_btn.pack(side="right")

    def create_progress_section(self, parent):
        """Create progress section"""
        self.progress_frame = GlowingFrame(parent, fg_color=self.colors["bg_medium"])
        self.progress_frame.pack(fill="x", pady=(0, 12))

        # Status row
        status_row = ctk.CTkFrame(self.progress_frame, fg_color="transparent")
        status_row.pack(fill="x", padx=20, pady=(12, 5))

        self.status_label = ctk.CTkLabel(
            status_row,
            text="Ready to download",
            font=ctk.CTkFont(size=12),
            text_color=self.colors["text_secondary"]
        )
        self.status_label.pack(side="left")

        self.speed_label = ctk.CTkLabel(
            status_row,
            text="",
            font=ctk.CTkFont(size=11),
            text_color=self.colors["accent_green"]
        )
        self.speed_label.pack(side="right")

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(
            self.progress_frame,
            height=10,
            corner_radius=5,
            progress_color=self.colors["accent_cyan"],
            fg_color=self.colors["bg_dark"]
        )
        self.progress_bar.pack(fill="x", padx=20, pady=(0, 5))
        self.progress_bar.set(0)

        # Progress info row
        info_row = ctk.CTkFrame(self.progress_frame, fg_color="transparent")
        info_row.pack(fill="x", padx=20, pady=(0, 12))

        self.progress_label = ctk.CTkLabel(
            info_row,
            text="0%",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=self.colors["accent_cyan"]
        )
        self.progress_label.pack(side="left")

        self.eta_label = ctk.CTkLabel(
            info_row,
            text="",
            font=ctk.CTkFont(size=11),
            text_color=self.colors["text_secondary"]
        )
        self.eta_label.pack(side="right")

    def create_log_section(self, parent):
        """Create log/output section"""
        log_frame = GlowingFrame(parent, fg_color=self.colors["bg_medium"])
        log_frame.pack(fill="both", expand=True)

        # Section title with clear button
        title_row = ctk.CTkFrame(log_frame, fg_color="transparent")
        title_row.pack(fill="x", padx=20, pady=(12, 5))

        log_title = ctk.CTkLabel(
            title_row,
            text="DOWNLOAD LOG",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.colors["accent_cyan"]
        )
        log_title.pack(side="left")

        clear_log_btn = ctk.CTkButton(
            title_row,
            text="Clear",
            command=self.clear_log,
            width=60,
            height=24,
            corner_radius=5,
            fg_color="transparent",
            hover_color=self.colors["bg_light"],
            border_width=1,
            border_color=self.colors["text_secondary"],
            font=ctk.CTkFont(size=10)
        )
        clear_log_btn.pack(side="right")

        # Log textbox
        self.log_text = ctk.CTkTextbox(
            log_frame,
            height=130,
            corner_radius=10,
            fg_color=self.colors["bg_dark"],
            font=ctk.CTkFont(family="Consolas", size=10),
            border_width=1,
            border_color=self.colors["bg_light"]
        )
        self.log_text.pack(fill="both", expand=True, padx=20, pady=(0, 12))

    def create_footer(self):
        """Create footer"""
        footer = ctk.CTkFrame(self.main_scroll, fg_color=self.colors["bg_medium"], height=35, corner_radius=0)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)

        footer_text = ctk.CTkLabel(
            footer,
            text=f"NeonTube v{__version__}  |  Supports 1000+ sites  |  Powered by yt-dlp",
            font=ctk.CTkFont(size=10),
            text_color=self.colors["text_secondary"]
        )
        footer_text.pack(expand=True)

    def animate_glow(self):
        """Animate the title glow effect"""
        colors = ["#00d4ff", "#00bbff", "#0099ff", "#00bbff"]
        self.glow_index = getattr(self, 'glow_index', 0)
        self.title_label.configure(text_color=colors[self.glow_index % len(colors)])
        self.glow_index += 1
        self.after(400, self.animate_glow)

    def on_type_change(self, value):
        """Handle Video/Audio type toggle"""
        if value == "Audio":
            self.format_menu.configure(values=self.audio_formats)
            self.format_var.set("mp3")
            self.quality_label.configure(text="AUDIO BITRATE")
            self.quality_menu.pack_forget()
            self.audio_quality_menu.pack(fill="x", pady=(4, 0))
        else:
            self.format_menu.configure(values=self.video_formats)
            self.format_var.set("mp4")
            self.quality_label.configure(text="VIDEO QUALITY")
            self.audio_quality_menu.pack_forget()
            self.quality_menu.pack(fill="x", pady=(4, 0))

    def paste_url(self):
        """Paste URL from clipboard"""
        try:
            clipboard = self.clipboard_get()
            self.url_entry.delete(0, "end")
            self.url_entry.insert(0, clipboard)
            self.log_message("URL pasted from clipboard", "info")
        except Exception:
            self.log_message("Failed to paste from clipboard", "error")

    def clear_url(self):
        """Clear the URL entry"""
        self.url_entry.delete(0, "end")

    def clear_log(self):
        """Clear the log textbox"""
        self.log_text.delete("1.0", "end")

    def browse_path(self):
        """Open folder browser"""
        path = filedialog.askdirectory(initialdir=self.download_path.get())
        if path:
            self.download_path.set(path)
            self.log_message(f"Save location: {path}", "info")

    def log_message(self, message, msg_type="info"):
        """Add message to log with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")

        type_colors = {
            "info": self.colors["text_secondary"],
            "success": self.colors["success"],
            "error": self.colors["error"],
            "warning": self.colors["warning"]
        }

        type_icons = {
            "info": "[*]",
            "success": "[+]",
            "error": "[!]",
            "warning": "[~]"
        }

        icon = type_icons.get(msg_type, "[*]")
        self.log_text.insert("end", f"{timestamp} {icon} {message}\n")
        self.log_text.see("end")

    def update_progress(self, progress, status="Downloading...", speed="", eta=""):
        """Update progress bar and status labels"""
        self.progress_bar.set(progress / 100)
        self.progress_label.configure(text=f"{progress:.1f}%")
        self.status_label.configure(text=status)
        self.speed_label.configure(text=speed)
        self.eta_label.configure(text=eta)

    def fetch_video_info(self):
        """Fetch and display video information"""
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Warning", "Please enter a URL first")
            return

        self.log_message("Fetching video info...", "info")

        def fetch():
            try:
                cmd = ["yt-dlp", "-j", "--no-download", url]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

                if result.returncode == 0:
                    info = json.loads(result.stdout)
                    title = info.get("title", "Unknown")
                    duration = info.get("duration", 0)
                    uploader = info.get("uploader", "Unknown")
                    view_count = info.get("view_count", 0)

                    # Format duration
                    mins, secs = divmod(duration, 60)
                    hours, mins = divmod(mins, 60)
                    duration_str = f"{hours:02d}:{mins:02d}:{secs:02d}" if hours else f"{mins:02d}:{secs:02d}"

                    # Format view count
                    if view_count >= 1_000_000:
                        views_str = f"{view_count/1_000_000:.1f}M views"
                    elif view_count >= 1_000:
                        views_str = f"{view_count/1_000:.1f}K views"
                    else:
                        views_str = f"{view_count} views"

                    self.after(0, lambda: self.log_message(f"Title: {title}", "success"))
                    self.after(0, lambda: self.log_message(f"Duration: {duration_str} | Uploader: {uploader}", "info"))
                    self.after(0, lambda: self.log_message(f"Views: {views_str}", "info"))
                else:
                    self.after(0, lambda: self.log_message(f"Failed to fetch info: {result.stderr}", "error"))

            except subprocess.TimeoutExpired:
                self.after(0, lambda: self.log_message("Request timed out", "error"))
            except json.JSONDecodeError:
                self.after(0, lambda: self.log_message("Failed to parse video info", "error"))
            except FileNotFoundError:
                self.after(0, lambda: self.log_message("yt-dlp not found. Please install it.", "error"))
            except Exception as e:
                self.after(0, lambda: self.log_message(f"Error: {str(e)}", "error"))

        threading.Thread(target=fetch, daemon=True).start()

    def validate_url(self, url):
        """Validate URL - accepts any URL since yt-dlp supports 1000+ sites"""
        # Basic URL pattern - yt-dlp will handle the rest
        url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        return bool(re.match(url_pattern, url))

    def check_for_updates(self):
        """Check for application updates"""
        self.log_message("Checking for updates...", "info")

        def check():
            try:
                from updater import Updater
                updater = Updater()
                has_update, latest_version, notes = updater.check_for_updates()

                if has_update:
                    self.after(0, lambda: self.show_update_dialog(latest_version, notes))
                else:
                    self.after(0, lambda: self.log_message(
                        f"You're running the latest version (v{__version__})", "success"
                    ))
            except ImportError:
                self.after(0, lambda: self.log_message(
                    "Update module not found", "warning"
                ))
            except Exception as e:
                self.after(0, lambda: self.log_message(
                    f"Update check failed: {str(e)}", "error"
                ))

        threading.Thread(target=check, daemon=True).start()

    def show_update_dialog(self, version, notes):
        """Show update available dialog"""
        result = messagebox.askyesno(
            "Update Available",
            f"NeonTube v{version} is available!\n\n"
            f"Current version: v{__version__}\n\n"
            f"Would you like to download the update?"
        )

        if result:
            import webbrowser
            webbrowser.open(
                "https://github.com/contactmukundthiru-cyber/Multi-Platform-Downloader/releases/latest"
            )
            self.log_message(f"Opening download page for v{version}...", "info")

    def start_download(self):
        """Start the download process"""
        url = self.url_entry.get().strip()

        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL")
            return

        if self.is_downloading:
            messagebox.showwarning("Warning", "Download already in progress")
            return

        if not self.validate_url(url):
            messagebox.showerror("Error", "Please enter a valid URL (must start with http:// or https://)")
            return

        # Check if output path exists
        output_path = self.download_path.get()
        if not os.path.isdir(output_path):
            messagebox.showerror("Error", f"Output directory does not exist: {output_path}")
            return

        self.is_downloading = True
        self.download_btn.configure(state="disabled", text="DOWNLOADING...")
        self.cancel_btn.configure(state="normal")
        self.update_progress(0, "Preparing download...")

        thread = threading.Thread(target=self.download_video, args=(url,), daemon=True)
        thread.start()

    def cancel_download(self):
        """Cancel the current download"""
        if self.current_process:
            self.current_process.terminate()
            self.log_message("Download cancelled by user", "warning")
            self.download_complete(False, "Download cancelled")

    def download_video(self, url):
        """Download video using yt-dlp"""
        try:
            self.after(0, lambda: self.log_message(f"Starting download: {url}", "info"))

            format_choice = self.format_var.get()
            video_quality = self.quality_var.get()
            audio_quality = self.audio_quality_var.get()
            output_path = self.download_path.get()

            # Build yt-dlp command
            output_template = os.path.join(output_path, "%(title)s.%(ext)s")
            cmd = ["yt-dlp", "--newline", "--progress"]

            # Audio formats
            if format_choice in self.audio_formats:
                audio_bitrate = audio_quality.split()[0]  # Extract number from "320 kbps"
                cmd.extend(["-x", "--audio-quality", f"{audio_bitrate}K"])
                cmd.extend(["--audio-format", format_choice])
                self.after(0, lambda: self.log_message(f"Audio: {format_choice.upper()} @ {audio_quality}", "info"))

            # Video formats
            elif format_choice in self.video_formats:
                # Parse quality
                height = None
                if "Best" not in video_quality:
                    # Extract resolution number
                    match = re.search(r'(\d+)p', video_quality)
                    if match:
                        height = match.group(1)

                if height:
                    cmd.extend(["-f", f"bestvideo[height<={height}]+bestaudio/best[height<={height}]/best"])
                else:
                    cmd.extend(["-f", "bestvideo+bestaudio/best"])

                cmd.extend(["--merge-output-format", format_choice])
                self.after(0, lambda: self.log_message(f"Video: {format_choice.upper()} @ {video_quality}", "info"))

            # Advanced options
            if self.download_subtitles.get():
                cmd.extend(["--write-subs", "--write-auto-subs", "--sub-lang", "en"])

            if self.download_thumbnail.get():
                cmd.append("--write-thumbnail")

            if self.embed_metadata.get():
                cmd.append("--embed-metadata")

            if self.prefer_ffmpeg.get():
                cmd.append("--prefer-ffmpeg")

            cmd.extend(["-o", output_template, url])

            # Log the command (for debugging)
            self.after(0, lambda: self.log_message(f"Command: yt-dlp ...", "info"))

            # Run yt-dlp
            self.current_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )

            # Parse output
            for line in self.current_process.stdout:
                line = line.strip()
                if not line:
                    continue

                # Extract progress info
                progress_match = re.search(r'(\d+\.?\d*)%', line)
                speed_match = re.search(r'at\s+([\d.]+\s*\w+/s)', line)
                eta_match = re.search(r'ETA\s+([\d:]+)', line)

                if progress_match:
                    progress = float(progress_match.group(1))
                    speed = speed_match.group(1) if speed_match else ""
                    eta = f"ETA: {eta_match.group(1)}" if eta_match else ""
                    self.after(0, lambda p=progress, s=speed, e=eta: self.update_progress(p, "Downloading...", s, e))

                # Log important messages
                if any(x in line for x in ["[download]", "[ExtractAudio]", "[Merger]", "[ffmpeg]", "Destination"]):
                    # Truncate long lines
                    display_line = line[:100] + "..." if len(line) > 100 else line
                    self.after(0, lambda l=display_line: self.log_message(l, "info"))

            self.current_process.wait()

            if self.current_process.returncode == 0:
                self.after(0, lambda: self.download_complete(True))
            else:
                self.after(0, lambda: self.download_complete(False, "Download failed - check log for details"))

        except FileNotFoundError:
            self.after(0, lambda: self.download_complete(False, "yt-dlp not found. Please install: pip install yt-dlp"))
        except Exception as e:
            self.after(0, lambda: self.download_complete(False, str(e)))
        finally:
            self.current_process = None

    def download_complete(self, success, error_msg=None):
        """Handle download completion"""
        self.is_downloading = False
        self.download_btn.configure(state="normal", text="DOWNLOAD")
        self.cancel_btn.configure(state="disabled")

        if success:
            self.update_progress(100, "Download complete!", "", "")
            self.log_message("Download completed successfully!", "success")
            self.progress_bar.configure(progress_color=self.colors["success"])
        else:
            self.update_progress(0, "Download failed", "", "")
            self.log_message(f"Failed: {error_msg}", "error")
            self.progress_bar.configure(progress_color=self.colors["error"])

        # Reset progress bar color after 3 seconds
        self.after(3000, lambda: self.progress_bar.configure(progress_color=self.colors["accent_cyan"]))

    def on_closing(self):
        """Handle window close event"""
        if self.is_downloading:
            if messagebox.askyesno("Confirm Exit", "Download in progress. Cancel and exit?"):
                if self.current_process:
                    self.current_process.terminate()
                self.destroy()
        else:
            self.destroy()


def main():
    """Main entry point"""
    app = YouTubeDownloader()
    app.mainloop()


if __name__ == "__main__":
    main()
