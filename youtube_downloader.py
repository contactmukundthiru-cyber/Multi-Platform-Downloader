#!/usr/bin/env python3
"""
Flare Download - Premium Multi-Platform Video Downloader
Part of the Flare ecosystem
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import os
import re
import subprocess
import json
from datetime import datetime
from typing import Optional, Callable
import math

# Version
try:
    from version import __version__
except ImportError:
    __version__ = "2.4.0"

# Configure appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


# ============================================================================
# FLARE DESIGN SYSTEM - Exact colors from Flare website
# ============================================================================
class Flare:
    """Flare Design System - Premium color palette and styling"""

    # Void - Deep blacks for backgrounds
    VOID_PURE = "#000000"
    VOID_DEEP = "#050505"
    VOID_DARK = "#0a0a0a"
    VOID_MEDIUM = "#111111"
    VOID_LIGHT = "#1a1a1a"
    VOID_SURFACE = "#222222"
    VOID_BORDER = "#2a2a2a"
    VOID_HOVER = "#333333"

    # Fire - Primary accent colors
    FIRE_BLOOD = "#8b0000"
    FIRE_CRIMSON = "#dc143c"
    FIRE_RED = "#ff2d2d"
    FIRE_FLAME = "#ff4500"
    FIRE_ORANGE = "#ff6b35"
    FIRE_TANGERINE = "#ff8c00"
    FIRE_AMBER = "#ffa500"
    FIRE_GOLD = "#ffc107"
    FIRE_YELLOW = "#ffeb3b"

    # Ember - Gradient accents
    EMBER_CORE = "#ff4500"
    EMBER_MID = "#ff6b35"
    EMBER_OUTER = "#ff8c00"

    # Text colors
    TEXT_PRIMARY = "#ffffff"
    TEXT_SECONDARY = "#a8a8a8"
    TEXT_MUTED = "#666666"
    TEXT_DISABLED = "#444444"

    # Status colors
    SUCCESS = "#22c55e"
    WARNING = "#f59e0b"
    ERROR = "#ef4444"
    INFO = "#3b82f6"

    # Fonts (fallbacks for cross-platform)
    FONT_DISPLAY = ("Segoe UI", "Arial", "Helvetica")
    FONT_MONO = ("Consolas", "Monaco", "Courier New")

    # Sizing
    RADIUS_SM = 8
    RADIUS_MD = 12
    RADIUS_LG = 16
    RADIUS_XL = 24


# ============================================================================
# CUSTOM WIDGETS - Premium styled components
# ============================================================================
class FlareButton(ctk.CTkButton):
    """Premium button with Flare styling"""

    def __init__(self, master, variant="primary", size="md", **kwargs):
        # Default styling based on variant
        styles = {
            "primary": {
                "fg_color": Flare.FIRE_FLAME,
                "hover_color": Flare.FIRE_ORANGE,
                "text_color": Flare.TEXT_PRIMARY,
                "border_width": 0,
            },
            "secondary": {
                "fg_color": Flare.VOID_SURFACE,
                "hover_color": Flare.VOID_HOVER,
                "text_color": Flare.TEXT_PRIMARY,
                "border_width": 1,
                "border_color": Flare.VOID_BORDER,
            },
            "ghost": {
                "fg_color": "transparent",
                "hover_color": Flare.VOID_HOVER,
                "text_color": Flare.TEXT_SECONDARY,
                "border_width": 0,
            },
            "danger": {
                "fg_color": Flare.ERROR,
                "hover_color": "#dc2626",
                "text_color": Flare.TEXT_PRIMARY,
                "border_width": 0,
            },
            "outline": {
                "fg_color": "transparent",
                "hover_color": Flare.FIRE_FLAME,
                "text_color": Flare.FIRE_FLAME,
                "border_width": 2,
                "border_color": Flare.FIRE_FLAME,
            },
        }

        sizes = {
            "sm": {"height": 32, "corner_radius": Flare.RADIUS_SM, "font_size": 12},
            "md": {"height": 40, "corner_radius": Flare.RADIUS_MD, "font_size": 13},
            "lg": {"height": 48, "corner_radius": Flare.RADIUS_MD, "font_size": 14},
            "xl": {"height": 56, "corner_radius": Flare.RADIUS_LG, "font_size": 16},
        }

        style = styles.get(variant, styles["primary"])
        sz = sizes.get(size, sizes["md"])

        # Merge with user kwargs
        final_kwargs = {
            **style,
            "height": sz["height"],
            "corner_radius": sz["corner_radius"],
            "font": ctk.CTkFont(size=sz["font_size"], weight="bold"),
            **kwargs
        }

        super().__init__(master, **final_kwargs)


class FlareInput(ctk.CTkEntry):
    """Premium input field with Flare styling"""

    def __init__(self, master, size="md", **kwargs):
        sizes = {
            "sm": {"height": 36, "font_size": 12},
            "md": {"height": 44, "font_size": 13},
            "lg": {"height": 52, "font_size": 14},
        }
        sz = sizes.get(size, sizes["md"])

        default_kwargs = {
            "height": sz["height"],
            "corner_radius": Flare.RADIUS_MD,
            "border_width": 1,
            "border_color": Flare.VOID_BORDER,
            "fg_color": Flare.VOID_DARK,
            "text_color": Flare.TEXT_PRIMARY,
            "placeholder_text_color": Flare.TEXT_MUTED,
            "font": ctk.CTkFont(size=sz["font_size"]),
        }

        super().__init__(master, **{**default_kwargs, **kwargs})

        # Focus effects
        self.bind("<FocusIn>", lambda e: self.configure(border_color=Flare.FIRE_FLAME))
        self.bind("<FocusOut>", lambda e: self.configure(border_color=Flare.VOID_BORDER))


class FlareCard(ctk.CTkFrame):
    """Premium card component with Flare styling"""

    def __init__(self, master, glow=False, **kwargs):
        default_kwargs = {
            "fg_color": Flare.VOID_MEDIUM,
            "corner_radius": Flare.RADIUS_LG,
            "border_width": 1,
            "border_color": Flare.VOID_BORDER,
        }

        super().__init__(master, **{**default_kwargs, **kwargs})

        if glow:
            self.configure(border_color=Flare.FIRE_FLAME)


class FlareSelect(ctk.CTkOptionMenu):
    """Premium dropdown with Flare styling"""

    def __init__(self, master, **kwargs):
        default_kwargs = {
            "height": 40,
            "corner_radius": Flare.RADIUS_MD,
            "fg_color": Flare.VOID_DARK,
            "button_color": Flare.FIRE_FLAME,
            "button_hover_color": Flare.FIRE_ORANGE,
            "dropdown_fg_color": Flare.VOID_MEDIUM,
            "dropdown_hover_color": Flare.FIRE_FLAME,
            "dropdown_text_color": Flare.TEXT_PRIMARY,
            "font": ctk.CTkFont(size=13),
        }

        super().__init__(master, **{**default_kwargs, **kwargs})


# ============================================================================
# MAIN APPLICATION
# ============================================================================
class FlareDownloader(ctk.CTk):
    """Flare Download - Premium Video Downloader"""

    def __init__(self):
        super().__init__()

        # Window setup
        self.title(f"Flare Download v{__version__}")
        self.geometry("900x800")
        self.minsize(800, 700)
        self.configure(fg_color=Flare.VOID_PURE)

        # State
        self.is_downloading = False
        self.process: Optional[subprocess.Popen] = None

        # Variables
        self.url_var = ctk.StringVar()
        self.output_dir = ctk.StringVar(value=os.path.expanduser("~/Downloads"))
        self.media_type = ctk.StringVar(value="video")
        self.format_var = ctk.StringVar(value="mp4")
        self.quality_var = ctk.StringVar(value="Best")

        # Options
        self.video_formats = ["mp4", "webm", "mkv"]
        self.audio_formats = ["mp3", "m4a", "wav", "flac", "opus"]
        self.video_qualities = ["Best", "4K", "1080p", "720p", "480p", "360p"]
        self.audio_qualities = ["Best", "320kbps", "256kbps", "192kbps", "128kbps"]

        # Build UI
        self._create_ui()

        # Window close handler
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _create_ui(self):
        """Build the premium UI"""
        # Main container
        self.main = ctk.CTkFrame(self, fg_color="transparent")
        self.main.pack(fill="both", expand=True, padx=24, pady=24)

        # Header
        self._create_header()

        # Content
        self._create_content()

        # Footer
        self._create_footer()

    def _create_header(self):
        """Create premium header"""
        header = ctk.CTkFrame(self.main, fg_color="transparent", height=80)
        header.pack(fill="x", pady=(0, 24))
        header.pack_propagate(False)

        # Logo
        logo_frame = ctk.CTkFrame(header, fg_color="transparent")
        logo_frame.pack(side="left", fill="y")

        # Fire icon (using text as fallback)
        fire_icon = ctk.CTkLabel(
            logo_frame,
            text="",
            font=ctk.CTkFont(size=32),
            text_color=Flare.FIRE_FLAME
        )
        fire_icon.pack(side="left", padx=(0, 12))

        # Title
        title_frame = ctk.CTkFrame(logo_frame, fg_color="transparent")
        title_frame.pack(side="left")

        title = ctk.CTkLabel(
            title_frame,
            text="FLARE",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=Flare.FIRE_FLAME
        )
        title.pack(side="left")

        title2 = ctk.CTkLabel(
            title_frame,
            text="DOWNLOAD",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=Flare.TEXT_PRIMARY
        )
        title2.pack(side="left", padx=(8, 0))

        # Subtitle
        subtitle = ctk.CTkLabel(
            logo_frame,
            text="Multi-Platform Video Downloader",
            font=ctk.CTkFont(size=11),
            text_color=Flare.TEXT_MUTED
        )
        subtitle.pack(side="left", padx=(16, 0), pady=(8, 0))

        # Version badge
        version = ctk.CTkLabel(
            header,
            text=f"v{__version__}",
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=Flare.VOID_SURFACE,
            corner_radius=6,
            text_color=Flare.TEXT_SECONDARY,
            padx=12,
            pady=4
        )
        version.pack(side="right")

    def _create_content(self):
        """Create main content area"""
        # Scrollable container
        content = ctk.CTkScrollableFrame(
            self.main,
            fg_color="transparent",
            scrollbar_button_color=Flare.VOID_HOVER,
            scrollbar_button_hover_color=Flare.FIRE_FLAME
        )
        content.pack(fill="both", expand=True)

        # URL Section
        self._create_url_section(content)

        # Options Section
        self._create_options_section(content)

        # Action Section
        self._create_action_section(content)

        # Progress Section
        self._create_progress_section(content)

        # Log Section
        self._create_log_section(content)

    def _create_url_section(self, parent):
        """Create URL input section"""
        card = FlareCard(parent, glow=True)
        card.pack(fill="x", pady=(0, 16))

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=20, pady=20)

        # Label
        label = ctk.CTkLabel(
            inner,
            text="VIDEO URL",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=Flare.FIRE_FLAME
        )
        label.pack(anchor="w", pady=(0, 8))

        # Input row
        input_row = ctk.CTkFrame(inner, fg_color="transparent")
        input_row.pack(fill="x")

        self.url_entry = FlareInput(
            input_row,
            size="lg",
            textvariable=self.url_var,
            placeholder_text="Paste video URL (YouTube, TikTok, Instagram, Twitter...)"
        )
        self.url_entry.pack(side="left", fill="x", expand=True, padx=(0, 12))

        # Buttons
        paste_btn = FlareButton(
            input_row,
            text="Paste",
            variant="secondary",
            size="lg",
            width=80,
            command=self._paste_url
        )
        paste_btn.pack(side="left", padx=(0, 8))

        clear_btn = FlareButton(
            input_row,
            text="Clear",
            variant="ghost",
            size="lg",
            width=80,
            command=self._clear_url
        )
        clear_btn.pack(side="left")

        # Platforms info
        platforms = ctk.CTkLabel(
            inner,
            text="Supports: YouTube, TikTok, Instagram, Twitter/X, Facebook, Vimeo, Reddit + 1000 more",
            font=ctk.CTkFont(size=10),
            text_color=Flare.TEXT_MUTED
        )
        platforms.pack(anchor="w", pady=(12, 0))

    def _create_options_section(self, parent):
        """Create options section"""
        card = FlareCard(parent)
        card.pack(fill="x", pady=(0, 16))

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=20, pady=20)

        # Label
        label = ctk.CTkLabel(
            inner,
            text="DOWNLOAD OPTIONS",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=Flare.FIRE_ORANGE
        )
        label.pack(anchor="w", pady=(0, 16))

        # Options grid
        grid = ctk.CTkFrame(inner, fg_color="transparent")
        grid.pack(fill="x")
        grid.columnconfigure((0, 1, 2), weight=1, uniform="col")

        # Media Type
        type_frame = ctk.CTkFrame(grid, fg_color="transparent")
        type_frame.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        ctk.CTkLabel(
            type_frame,
            text="Type",
            font=ctk.CTkFont(size=10),
            text_color=Flare.TEXT_SECONDARY
        ).pack(anchor="w", pady=(0, 4))

        self.type_selector = ctk.CTkSegmentedButton(
            type_frame,
            values=["Video", "Audio"],
            command=self._on_type_change,
            height=40,
            corner_radius=Flare.RADIUS_MD,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=Flare.VOID_DARK,
            selected_color=Flare.FIRE_FLAME,
            selected_hover_color=Flare.FIRE_ORANGE,
            unselected_color=Flare.VOID_SURFACE,
            unselected_hover_color=Flare.VOID_HOVER
        )
        self.type_selector.set("Video")
        self.type_selector.pack(fill="x")

        # Format
        format_frame = ctk.CTkFrame(grid, fg_color="transparent")
        format_frame.grid(row=0, column=1, sticky="ew", padx=8)

        ctk.CTkLabel(
            format_frame,
            text="Format",
            font=ctk.CTkFont(size=10),
            text_color=Flare.TEXT_SECONDARY
        ).pack(anchor="w", pady=(0, 4))

        self.format_select = FlareSelect(
            format_frame,
            values=self.video_formats,
            variable=self.format_var
        )
        self.format_select.pack(fill="x")

        # Quality
        quality_frame = ctk.CTkFrame(grid, fg_color="transparent")
        quality_frame.grid(row=0, column=2, sticky="ew", padx=(8, 0))

        ctk.CTkLabel(
            quality_frame,
            text="Quality",
            font=ctk.CTkFont(size=10),
            text_color=Flare.TEXT_SECONDARY
        ).pack(anchor="w", pady=(0, 4))

        self.quality_select = FlareSelect(
            quality_frame,
            values=self.video_qualities,
            variable=self.quality_var
        )
        self.quality_select.pack(fill="x")

        # Output path
        path_frame = ctk.CTkFrame(inner, fg_color="transparent")
        path_frame.pack(fill="x", pady=(16, 0))

        ctk.CTkLabel(
            path_frame,
            text="Save to",
            font=ctk.CTkFont(size=10),
            text_color=Flare.TEXT_SECONDARY
        ).pack(anchor="w", pady=(0, 4))

        path_row = ctk.CTkFrame(path_frame, fg_color="transparent")
        path_row.pack(fill="x")

        self.path_entry = FlareInput(
            path_row,
            textvariable=self.output_dir
        )
        self.path_entry.pack(side="left", fill="x", expand=True, padx=(0, 12))

        browse_btn = FlareButton(
            path_row,
            text="Browse",
            variant="secondary",
            width=100,
            command=self._browse_folder
        )
        browse_btn.pack(side="right")

    def _create_action_section(self, parent):
        """Create action buttons"""
        action = ctk.CTkFrame(parent, fg_color="transparent")
        action.pack(fill="x", pady=(0, 16))

        # Download button
        self.download_btn = FlareButton(
            action,
            text="DOWNLOAD",
            variant="primary",
            size="xl",
            command=self._start_download
        )
        self.download_btn.pack(side="left", fill="x", expand=True, padx=(0, 12))

        # Cancel button
        self.cancel_btn = FlareButton(
            action,
            text="Cancel",
            variant="danger",
            size="xl",
            width=100,
            state="disabled",
            command=self._cancel_download
        )
        self.cancel_btn.pack(side="right")

    def _create_progress_section(self, parent):
        """Create progress display"""
        self.progress_card = FlareCard(parent)
        self.progress_card.pack(fill="x", pady=(0, 16))

        inner = ctk.CTkFrame(self.progress_card, fg_color="transparent")
        inner.pack(fill="x", padx=20, pady=20)

        # Status row
        status_row = ctk.CTkFrame(inner, fg_color="transparent")
        status_row.pack(fill="x", pady=(0, 12))

        self.status_label = ctk.CTkLabel(
            status_row,
            text="Ready",
            font=ctk.CTkFont(size=13),
            text_color=Flare.TEXT_SECONDARY
        )
        self.status_label.pack(side="left")

        self.speed_label = ctk.CTkLabel(
            status_row,
            text="",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=Flare.FIRE_GOLD
        )
        self.speed_label.pack(side="right")

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(
            inner,
            height=8,
            corner_radius=4,
            progress_color=Flare.FIRE_FLAME,
            fg_color=Flare.VOID_DARK
        )
        self.progress_bar.pack(fill="x", pady=(0, 8))
        self.progress_bar.set(0)

        # Info row
        info_row = ctk.CTkFrame(inner, fg_color="transparent")
        info_row.pack(fill="x")

        self.percent_label = ctk.CTkLabel(
            info_row,
            text="0%",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=Flare.FIRE_FLAME
        )
        self.percent_label.pack(side="left")

        self.eta_label = ctk.CTkLabel(
            info_row,
            text="",
            font=ctk.CTkFont(size=11),
            text_color=Flare.TEXT_MUTED
        )
        self.eta_label.pack(side="right")

    def _create_log_section(self, parent):
        """Create log display"""
        card = FlareCard(parent)
        card.pack(fill="both", expand=True)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=20, pady=20)

        # Header
        header = ctk.CTkFrame(inner, fg_color="transparent")
        header.pack(fill="x", pady=(0, 8))

        ctk.CTkLabel(
            header,
            text="LOG",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=Flare.TEXT_SECONDARY
        ).pack(side="left")

        clear_btn = FlareButton(
            header,
            text="Clear",
            variant="ghost",
            size="sm",
            width=60,
            command=self._clear_log
        )
        clear_btn.pack(side="right")

        # Log text
        self.log_text = ctk.CTkTextbox(
            inner,
            height=120,
            corner_radius=Flare.RADIUS_MD,
            fg_color=Flare.VOID_DARK,
            text_color=Flare.TEXT_SECONDARY,
            font=ctk.CTkFont(family="Consolas", size=11),
            border_width=1,
            border_color=Flare.VOID_BORDER
        )
        self.log_text.pack(fill="both", expand=True)

    def _create_footer(self):
        """Create footer"""
        footer = ctk.CTkFrame(self.main, fg_color="transparent", height=32)
        footer.pack(fill="x", pady=(16, 0))

        text = ctk.CTkLabel(
            footer,
            text="Part of the Flare ecosystem  •  Powered by yt-dlp",
            font=ctk.CTkFont(size=10),
            text_color=Flare.TEXT_MUTED
        )
        text.pack(expand=True)

    # ========================================================================
    # EVENT HANDLERS
    # ========================================================================

    def _paste_url(self):
        """Paste from clipboard"""
        try:
            url = self.clipboard_get()
            self.url_var.set(url)
            self._log("URL pasted", "info")
        except:
            self._log("Failed to paste from clipboard", "error")

    def _clear_url(self):
        """Clear URL"""
        self.url_var.set("")

    def _clear_log(self):
        """Clear log"""
        self.log_text.delete("1.0", "end")

    def _browse_folder(self):
        """Browse for output folder"""
        folder = filedialog.askdirectory(initialdir=self.output_dir.get())
        if folder:
            self.output_dir.set(folder)
            self._log(f"Output: {folder}", "info")

    def _on_type_change(self, value):
        """Handle media type change"""
        if value == "Audio":
            self.format_select.configure(values=self.audio_formats)
            self.format_var.set("mp3")
            self.quality_select.configure(values=self.audio_qualities)
            self.quality_var.set("Best")
        else:
            self.format_select.configure(values=self.video_formats)
            self.format_var.set("mp4")
            self.quality_select.configure(values=self.video_qualities)
            self.quality_var.set("Best")

    def _log(self, message: str, level: str = "info"):
        """Add to log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        icons = {"info": "•", "success": "✓", "error": "✗", "warning": "!"}
        icon = icons.get(level, "•")
        self.log_text.insert("end", f"[{timestamp}] {icon} {message}\n")
        self.log_text.see("end")

    def _update_progress(self, percent: float, status: str = "", speed: str = "", eta: str = ""):
        """Update progress UI"""
        self.progress_bar.set(percent / 100)
        self.percent_label.configure(text=f"{percent:.0f}%")
        if status:
            self.status_label.configure(text=status)
        if speed:
            self.speed_label.configure(text=speed)
        if eta:
            self.eta_label.configure(text=f"ETA: {eta}")

    def _set_downloading(self, state: bool):
        """Set downloading state"""
        self.is_downloading = state
        if state:
            self.download_btn.configure(state="disabled", text="Downloading...")
            self.cancel_btn.configure(state="normal")
            self.progress_bar.configure(progress_color=Flare.FIRE_FLAME)
        else:
            self.download_btn.configure(state="normal", text="DOWNLOAD")
            self.cancel_btn.configure(state="disabled")

    # ========================================================================
    # DOWNLOAD FUNCTIONALITY
    # ========================================================================

    def _start_download(self):
        """Start download"""
        url = self.url_var.get().strip()

        if not url:
            messagebox.showerror("Error", "Please enter a URL")
            return

        if not re.match(r'^https?://', url):
            messagebox.showerror("Error", "Invalid URL - must start with http:// or https://")
            return

        if not os.path.isdir(self.output_dir.get()):
            messagebox.showerror("Error", "Output folder does not exist")
            return

        self._set_downloading(True)
        self._update_progress(0, "Starting...")
        self._log(f"Starting download: {url[:60]}...", "info")

        thread = threading.Thread(target=self._download_thread, args=(url,), daemon=True)
        thread.start()

    def _cancel_download(self):
        """Cancel current download"""
        if self.process:
            self.process.terminate()
            self._log("Download cancelled", "warning")
            self._download_finished(False, "Cancelled")

    def _download_thread(self, url: str):
        """Download in background thread"""
        try:
            output_dir = self.output_dir.get()
            fmt = self.format_var.get()
            quality = self.quality_var.get()
            is_audio = self.type_selector.get() == "Audio"

            # Build output template
            output_template = os.path.join(output_dir, "%(title)s.%(ext)s")

            # Build yt-dlp command
            cmd = [
                "yt-dlp",
                "--newline",
                "--progress",
                "--no-warnings",
                "--no-playlist",
                "--restrict-filenames",
            ]

            if is_audio:
                # Audio extraction
                cmd.extend(["-x", "--audio-format", fmt])

                if quality != "Best":
                    bitrate = quality.replace("kbps", "")
                    cmd.extend(["--audio-quality", f"{bitrate}K"])

                self.after(0, lambda: self._log(f"Audio: {fmt.upper()} @ {quality}", "info"))
            else:
                # Video download
                if quality == "Best":
                    cmd.extend(["-f", "bestvideo+bestaudio/best"])
                elif quality == "4K":
                    cmd.extend(["-f", "bestvideo[height<=2160]+bestaudio/best[height<=2160]/best"])
                else:
                    height = quality.replace("p", "")
                    cmd.extend(["-f", f"bestvideo[height<={height}]+bestaudio/best[height<={height}]/best"])

                cmd.extend(["--merge-output-format", fmt])
                self.after(0, lambda: self._log(f"Video: {fmt.upper()} @ {quality}", "info"))

            cmd.extend(["-o", output_template, url])

            # Run yt-dlp
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )

            # Parse output
            for line in self.process.stdout:
                line = line.strip()
                if not line:
                    continue

                # Parse progress
                progress = re.search(r'(\d+\.?\d*)%', line)
                speed = re.search(r'at\s+([\d.]+\s*\w+/s)', line)
                eta = re.search(r'ETA\s+([\d:]+)', line)

                if progress:
                    pct = float(progress.group(1))
                    spd = speed.group(1) if speed else ""
                    et = eta.group(1) if eta else ""
                    self.after(0, lambda p=pct, s=spd, e=et: self._update_progress(p, "Downloading...", s, e))

                # Log important lines
                if any(x in line.lower() for x in ["destination:", "downloading", "merging", "deleting"]):
                    short = line[:70] + "..." if len(line) > 70 else line
                    self.after(0, lambda l=short: self._log(l, "info"))

            self.process.wait()

            success = self.process.returncode == 0
            self.after(0, lambda: self._download_finished(success))

        except FileNotFoundError:
            self.after(0, lambda: self._download_finished(False, "yt-dlp not found"))
        except Exception as e:
            self.after(0, lambda: self._download_finished(False, str(e)[:50]))
        finally:
            self.process = None

    def _download_finished(self, success: bool, error: str = None):
        """Handle download completion"""
        self._set_downloading(False)

        if success:
            self._update_progress(100, "Complete!", "", "")
            self._log("Download completed!", "success")
            self.progress_bar.configure(progress_color=Flare.SUCCESS)
        else:
            self._update_progress(0, "Failed", "", "")
            self._log(f"Failed: {error or 'Unknown error'}", "error")
            self.progress_bar.configure(progress_color=Flare.ERROR)

        # Reset color after delay
        self.after(3000, lambda: self.progress_bar.configure(progress_color=Flare.FIRE_FLAME))

    def _on_close(self):
        """Handle window close"""
        if self.is_downloading:
            if messagebox.askyesno("Confirm", "Download in progress. Cancel and exit?"):
                if self.process:
                    self.process.terminate()
                self.destroy()
        else:
            self.destroy()


# ============================================================================
# MAIN
# ============================================================================

def main():
    app = FlareDownloader()
    app.mainloop()


if __name__ == "__main__":
    main()
