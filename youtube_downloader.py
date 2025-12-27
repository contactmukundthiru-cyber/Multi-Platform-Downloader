#!/usr/bin/env python3
"""
Flare Download - Multi-Platform Video Downloader
Premium cinematic UI with fire/ember theme
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
from typing import Optional
import math

# Version info
try:
    from version import __version__
except ImportError:
    __version__ = "2.3.0"

# Set appearance mode and default color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class FlareColors:
    """Flare brand color palette"""
    # Void (backgrounds) - deep blacks
    VOID_DEEP = "#050505"
    VOID_DARK = "#0a0a0a"
    VOID_MEDIUM = "#111111"
    VOID_LIGHT = "#1a1a1a"
    VOID_SURFACE = "#222222"
    VOID_BORDER = "#2a2a2a"
    VOID_HOVER = "#333333"

    # Fire (primary accents)
    FIRE_RED = "#ff2d2d"
    FIRE_FLAME = "#ff4500"
    FIRE_ORANGE = "#ff6b35"
    FIRE_TANGERINE = "#ff8c00"
    FIRE_AMBER = "#ffa500"
    FIRE_GOLD = "#ffc107"

    # Ember (secondary accents)
    EMBER_CORE = "#ff4500"
    EMBER_MID = "#ff6b35"
    EMBER_OUTER = "#ff8c00"
    EMBER_GLOW = "#ff450033"

    # Text
    TEXT_PRIMARY = "#ffffff"
    TEXT_SECONDARY = "#a0a0a0"
    TEXT_MUTED = "#666666"
    TEXT_FIRE = "#ff6b35"

    # Status
    SUCCESS = "#22c55e"
    WARNING = "#f59e0b"
    ERROR = "#ef4444"
    INFO = "#3b82f6"


class AnimatedButton(ctk.CTkButton):
    """Button with hover glow and press animation"""
    def __init__(self, master, glow_color=FlareColors.FIRE_FLAME, **kwargs):
        self.glow_color = glow_color
        self.original_fg = kwargs.get('fg_color', FlareColors.FIRE_FLAME)
        super().__init__(master, **kwargs)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)

    def _on_enter(self, event):
        if self.cget("state") != "disabled":
            self.configure(border_width=2, border_color=self.glow_color)

    def _on_leave(self, event):
        self.configure(border_width=0)

    def _on_press(self, event):
        if self.cget("state") != "disabled":
            # Slight scale effect via color shift
            self.configure(fg_color=self._darken_color(self.original_fg))

    def _on_release(self, event):
        if self.cget("state") != "disabled":
            self.configure(fg_color=self.original_fg)

    def _darken_color(self, hex_color):
        """Darken a hex color by 20%"""
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        darkened = tuple(int(c * 0.8) for c in rgb)
        return f"#{darkened[0]:02x}{darkened[1]:02x}{darkened[2]:02x}"


class GlowFrame(ctk.CTkFrame):
    """Frame with animated glow border"""
    def __init__(self, master, glow_color=FlareColors.FIRE_FLAME, animate=False, **kwargs):
        if 'border_width' not in kwargs:
            kwargs['border_width'] = 1
        if 'border_color' not in kwargs:
            kwargs['border_color'] = glow_color
        super().__init__(master, **kwargs)
        self.glow_color = glow_color
        self.animate_glow = animate
        self.glow_phase = 0
        if animate:
            self._pulse_glow()

    def _pulse_glow(self):
        """Create pulsing glow effect"""
        self.glow_phase += 0.1
        intensity = (math.sin(self.glow_phase) + 1) / 2
        # Interpolate between dim and bright
        alpha = int(40 + intensity * 60)
        self.configure(border_color=f"{self.glow_color}{alpha:02x}")
        self.after(50, self._pulse_glow)


class PulsingDot(ctk.CTkFrame):
    """Animated status indicator dot"""
    def __init__(self, master, color=FlareColors.FIRE_FLAME, size=10, **kwargs):
        super().__init__(master, width=size, height=size, corner_radius=size//2, fg_color=color, **kwargs)
        self.color = color
        self.phase = 0
        self._pulse()

    def _pulse(self):
        self.phase += 0.15
        scale = 0.7 + 0.3 * (math.sin(self.phase) + 1) / 2
        alpha = int(150 + 105 * (math.sin(self.phase) + 1) / 2)
        base_color = self.color.lstrip('#')
        r, g, b = int(base_color[0:2], 16), int(base_color[2:4], 16), int(base_color[4:6], 16)
        r = min(255, int(r * scale + 50))
        g = min(255, int(g * scale))
        b = min(255, int(b * scale))
        self.configure(fg_color=f"#{r:02x}{g:02x}{b:02x}")
        self.after(50, self._pulse)


class FlareDownloader(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window configuration
        self.title(f"Flare Download v{__version__}")
        self.geometry("1000x900")
        self.minsize(900, 800)
        self.configure(fg_color=FlareColors.VOID_DEEP)

        # Supported platforms
        self.supported_platforms = [
            "YouTube", "TikTok", "Instagram", "Twitter/X", "Facebook",
            "Vimeo", "Dailymotion", "Twitch", "Reddit", "SoundCloud"
        ]

        # Variables
        self.download_path = ctk.StringVar(value=os.path.expanduser("~/Downloads"))
        self.format_var = ctk.StringVar(value="mp4")
        self.quality_var = ctk.StringVar(value="Best Quality")
        self.audio_quality_var = ctk.StringVar(value="320 kbps")
        self.type_var = ctk.StringVar(value="Video")
        self.is_downloading = False
        self.current_process: Optional[subprocess.Popen] = None

        # Options
        self.download_subtitles = ctk.BooleanVar(value=False)
        self.download_thumbnail = ctk.BooleanVar(value=False)
        self.embed_metadata = ctk.BooleanVar(value=True)

        # Quality options
        self.video_qualities = [
            "Best Quality", "4K (2160p)", "2K (1440p)", "1080p (Full HD)",
            "720p (HD)", "480p", "360p", "240p", "144p"
        ]
        self.audio_qualities = [
            "320 kbps", "256 kbps", "192 kbps", "128 kbps", "96 kbps", "64 kbps"
        ]

        # Formats
        self.video_formats = ["mp4", "webm", "mkv", "avi", "mov"]
        self.audio_formats = ["mp3", "wav", "m4a", "flac", "aac", "opus", "ogg"]

        # Animation state
        self.fire_colors = [
            FlareColors.FIRE_FLAME, FlareColors.FIRE_ORANGE,
            FlareColors.FIRE_TANGERINE, FlareColors.FIRE_AMBER
        ]
        self.fire_index = 0

        # Build UI
        self._build_ui()

        # Start animations
        self._animate_title()

        # Bind close event
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _build_ui(self):
        """Build the complete UI"""
        # Main container with gradient effect
        self.main_container = ctk.CTkFrame(self, fg_color=FlareColors.VOID_DEEP)
        self.main_container.pack(fill="both", expand=True)

        # Scrollable content
        self.scroll_frame = ctk.CTkScrollableFrame(
            self.main_container,
            fg_color="transparent",
            scrollbar_button_color=FlareColors.FIRE_FLAME,
            scrollbar_button_hover_color=FlareColors.FIRE_ORANGE
        )
        self.scroll_frame.pack(fill="both", expand=True, padx=2, pady=2)

        self._create_header()
        self._create_url_section()
        self._create_options_section()
        self._create_advanced_section()
        self._create_action_section()
        self._create_progress_section()
        self._create_log_section()
        self._create_footer()

    def _create_header(self):
        """Create premium header with animated logo"""
        header = ctk.CTkFrame(self.scroll_frame, fg_color=FlareColors.VOID_DARK, height=100, corner_radius=0)
        header.pack(fill="x")
        header.pack_propagate(False)

        # Inner container
        header_inner = ctk.CTkFrame(header, fg_color="transparent")
        header_inner.pack(expand=True, fill="both", padx=40, pady=20)

        # Logo section
        logo_frame = ctk.CTkFrame(header_inner, fg_color="transparent")
        logo_frame.pack(side="left")

        # Fire icon indicator
        self.fire_dot = PulsingDot(logo_frame, FlareColors.FIRE_FLAME, size=12)
        self.fire_dot.pack(side="left", padx=(0, 12))

        # Animated title
        self.title_flare = ctk.CTkLabel(
            logo_frame,
            text="FLARE",
            font=ctk.CTkFont(family="Segoe UI", size=38, weight="bold"),
            text_color=FlareColors.FIRE_FLAME
        )
        self.title_flare.pack(side="left")

        self.title_download = ctk.CTkLabel(
            logo_frame,
            text="DOWNLOAD",
            font=ctk.CTkFont(family="Segoe UI", size=38, weight="bold"),
            text_color=FlareColors.TEXT_PRIMARY
        )
        self.title_download.pack(side="left", padx=(8, 0))

        # Subtitle with platform icons
        subtitle_frame = ctk.CTkFrame(header_inner, fg_color="transparent")
        subtitle_frame.pack(side="left", padx=(20, 0), pady=(10, 0))

        subtitle = ctk.CTkLabel(
            subtitle_frame,
            text="MULTI-PLATFORM VIDEO DOWNLOADER",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=FlareColors.TEXT_SECONDARY
        )
        subtitle.pack(anchor="w")

        platforms_text = " • ".join(self.supported_platforms[:5]) + " + 1000 more"
        platforms = ctk.CTkLabel(
            subtitle_frame,
            text=platforms_text,
            font=ctk.CTkFont(size=9),
            text_color=FlareColors.TEXT_MUTED
        )
        platforms.pack(anchor="w")

        # Right side - version and update
        right_frame = ctk.CTkFrame(header_inner, fg_color="transparent")
        right_frame.pack(side="right")

        # Update button
        update_btn = AnimatedButton(
            right_frame,
            text="Check Updates",
            command=self._check_updates,
            width=110,
            height=32,
            corner_radius=8,
            fg_color="transparent",
            text_color=FlareColors.TEXT_SECONDARY,
            hover_color=FlareColors.VOID_HOVER,
            font=ctk.CTkFont(size=11),
            glow_color=FlareColors.FIRE_ORANGE
        )
        update_btn.pack(side="left", padx=(0, 12))

        # Version badge
        version_badge = ctk.CTkLabel(
            right_frame,
            text=f"v{__version__}",
            font=ctk.CTkFont(size=10, weight="bold"),
            fg_color=FlareColors.FIRE_FLAME,
            text_color=FlareColors.VOID_DEEP,
            corner_radius=6,
            padx=10,
            pady=4
        )
        version_badge.pack(side="left")

    def _create_url_section(self):
        """Create URL input section with premium styling"""
        section = GlowFrame(
            self.scroll_frame,
            fg_color=FlareColors.VOID_MEDIUM,
            corner_radius=16,
            glow_color=FlareColors.FIRE_FLAME
        )
        section.pack(fill="x", padx=30, pady=(20, 12))

        # Section header
        header = ctk.CTkFrame(section, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(20, 12))

        # Title with icon
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(side="left")

        icon_label = ctk.CTkLabel(
            title_frame,
            text="🔗",
            font=ctk.CTkFont(size=16)
        )
        icon_label.pack(side="left", padx=(0, 8))

        title = ctk.CTkLabel(
            title_frame,
            text="VIDEO URL",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=FlareColors.FIRE_FLAME
        )
        title.pack(side="left")

        # Platform hint
        hint = ctk.CTkLabel(
            header,
            text="Paste any video URL from supported platforms",
            font=ctk.CTkFont(size=10),
            text_color=FlareColors.TEXT_MUTED
        )
        hint.pack(side="right")

        # URL input container
        input_container = ctk.CTkFrame(section, fg_color="transparent")
        input_container.pack(fill="x", padx=24, pady=(0, 16))

        # URL entry with glow effect
        self.url_entry = ctk.CTkEntry(
            input_container,
            placeholder_text="https://youtube.com/watch?v=... or any video URL",
            height=50,
            corner_radius=12,
            border_width=2,
            border_color=FlareColors.VOID_BORDER,
            fg_color=FlareColors.VOID_DARK,
            text_color=FlareColors.TEXT_PRIMARY,
            placeholder_text_color=FlareColors.TEXT_MUTED,
            font=ctk.CTkFont(size=13)
        )
        self.url_entry.pack(side="left", fill="x", expand=True, padx=(0, 12))
        self.url_entry.bind("<FocusIn>", lambda e: self.url_entry.configure(border_color=FlareColors.FIRE_FLAME))
        self.url_entry.bind("<FocusOut>", lambda e: self.url_entry.configure(border_color=FlareColors.VOID_BORDER))

        # Button group
        btn_group = ctk.CTkFrame(input_container, fg_color="transparent")
        btn_group.pack(side="right")

        paste_btn = AnimatedButton(
            btn_group,
            text="PASTE",
            command=self._paste_url,
            width=80,
            height=50,
            corner_radius=12,
            fg_color=FlareColors.FIRE_ORANGE,
            hover_color=FlareColors.FIRE_TANGERINE,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        paste_btn.pack(side="left", padx=(0, 8))

        clear_btn = AnimatedButton(
            btn_group,
            text="CLEAR",
            command=self._clear_url,
            width=80,
            height=50,
            corner_radius=12,
            fg_color=FlareColors.VOID_LIGHT,
            hover_color=FlareColors.ERROR,
            font=ctk.CTkFont(size=12, weight="bold"),
            glow_color=FlareColors.ERROR
        )
        clear_btn.pack(side="left")

        # Fetch info button
        info_btn = AnimatedButton(
            section,
            text="📊  FETCH VIDEO INFO",
            command=self._fetch_info,
            height=36,
            corner_radius=10,
            fg_color="transparent",
            text_color=FlareColors.FIRE_ORANGE,
            hover_color=FlareColors.VOID_HOVER,
            font=ctk.CTkFont(size=11, weight="bold"),
            glow_color=FlareColors.FIRE_ORANGE
        )
        info_btn.pack(anchor="e", padx=24, pady=(0, 20))

    def _create_options_section(self):
        """Create download options with premium controls"""
        section = GlowFrame(
            self.scroll_frame,
            fg_color=FlareColors.VOID_MEDIUM,
            corner_radius=16,
            glow_color=FlareColors.FIRE_ORANGE
        )
        section.pack(fill="x", padx=30, pady=(0, 12))

        # Header
        header = ctk.CTkFrame(section, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(20, 16))

        icon_label = ctk.CTkLabel(header, text="⚙️", font=ctk.CTkFont(size=16))
        icon_label.pack(side="left", padx=(0, 8))

        title = ctk.CTkLabel(
            header,
            text="DOWNLOAD OPTIONS",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=FlareColors.FIRE_ORANGE
        )
        title.pack(side="left")

        # Options grid
        grid = ctk.CTkFrame(section, fg_color="transparent")
        grid.pack(fill="x", padx=24, pady=(0, 20))
        grid.columnconfigure((0, 1, 2), weight=1, uniform="col")

        # Media Type
        type_frame = ctk.CTkFrame(grid, fg_color="transparent")
        type_frame.grid(row=0, column=0, sticky="ew", padx=(0, 12))

        ctk.CTkLabel(
            type_frame,
            text="MEDIA TYPE",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=FlareColors.TEXT_SECONDARY
        ).pack(anchor="w", pady=(0, 6))

        self.type_toggle = ctk.CTkSegmentedButton(
            type_frame,
            values=["Video", "Audio"],
            variable=self.type_var,
            command=self._on_type_change,
            height=42,
            corner_radius=10,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=FlareColors.VOID_DARK,
            selected_color=FlareColors.FIRE_FLAME,
            selected_hover_color=FlareColors.FIRE_ORANGE,
            unselected_color=FlareColors.VOID_LIGHT,
            unselected_hover_color=FlareColors.VOID_HOVER
        )
        self.type_toggle.pack(fill="x")

        # Format
        format_frame = ctk.CTkFrame(grid, fg_color="transparent")
        format_frame.grid(row=0, column=1, sticky="ew", padx=12)

        ctk.CTkLabel(
            format_frame,
            text="FORMAT",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=FlareColors.TEXT_SECONDARY
        ).pack(anchor="w", pady=(0, 6))

        self.format_menu = ctk.CTkOptionMenu(
            format_frame,
            values=self.video_formats,
            variable=self.format_var,
            height=42,
            corner_radius=10,
            font=ctk.CTkFont(size=12),
            fg_color=FlareColors.VOID_DARK,
            button_color=FlareColors.FIRE_FLAME,
            button_hover_color=FlareColors.FIRE_ORANGE,
            dropdown_fg_color=FlareColors.VOID_MEDIUM,
            dropdown_hover_color=FlareColors.FIRE_FLAME,
            dropdown_text_color=FlareColors.TEXT_PRIMARY
        )
        self.format_menu.pack(fill="x")

        # Quality
        quality_frame = ctk.CTkFrame(grid, fg_color="transparent")
        quality_frame.grid(row=0, column=2, sticky="ew", padx=(12, 0))

        self.quality_label = ctk.CTkLabel(
            quality_frame,
            text="QUALITY",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=FlareColors.TEXT_SECONDARY
        )
        self.quality_label.pack(anchor="w", pady=(0, 6))

        self.quality_menu = ctk.CTkOptionMenu(
            quality_frame,
            values=self.video_qualities,
            variable=self.quality_var,
            height=42,
            corner_radius=10,
            font=ctk.CTkFont(size=12),
            fg_color=FlareColors.VOID_DARK,
            button_color=FlareColors.FIRE_ORANGE,
            button_hover_color=FlareColors.FIRE_TANGERINE,
            dropdown_fg_color=FlareColors.VOID_MEDIUM,
            dropdown_hover_color=FlareColors.FIRE_ORANGE,
            dropdown_text_color=FlareColors.TEXT_PRIMARY
        )
        self.quality_menu.pack(fill="x")

        # Audio quality (hidden by default)
        self.audio_quality_menu = ctk.CTkOptionMenu(
            quality_frame,
            values=self.audio_qualities,
            variable=self.audio_quality_var,
            height=42,
            corner_radius=10,
            font=ctk.CTkFont(size=12),
            fg_color=FlareColors.VOID_DARK,
            button_color=FlareColors.FIRE_ORANGE,
            button_hover_color=FlareColors.FIRE_TANGERINE,
            dropdown_fg_color=FlareColors.VOID_MEDIUM,
            dropdown_hover_color=FlareColors.FIRE_ORANGE,
            dropdown_text_color=FlareColors.TEXT_PRIMARY
        )

        # Save location
        path_frame = ctk.CTkFrame(section, fg_color="transparent")
        path_frame.pack(fill="x", padx=24, pady=(0, 20))

        ctk.CTkLabel(
            path_frame,
            text="SAVE LOCATION",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=FlareColors.TEXT_SECONDARY
        ).pack(anchor="w", pady=(0, 6))

        path_input = ctk.CTkFrame(path_frame, fg_color="transparent")
        path_input.pack(fill="x")

        self.path_entry = ctk.CTkEntry(
            path_input,
            textvariable=self.download_path,
            height=42,
            corner_radius=10,
            border_width=1,
            border_color=FlareColors.VOID_BORDER,
            fg_color=FlareColors.VOID_DARK,
            font=ctk.CTkFont(size=12)
        )
        self.path_entry.pack(side="left", fill="x", expand=True, padx=(0, 12))

        browse_btn = AnimatedButton(
            path_input,
            text="📁  BROWSE",
            command=self._browse_path,
            width=100,
            height=42,
            corner_radius=10,
            fg_color=FlareColors.VOID_LIGHT,
            hover_color=FlareColors.FIRE_ORANGE,
            font=ctk.CTkFont(size=11, weight="bold"),
            glow_color=FlareColors.FIRE_ORANGE
        )
        browse_btn.pack(side="right")

    def _create_advanced_section(self):
        """Create advanced options with checkboxes"""
        section = GlowFrame(
            self.scroll_frame,
            fg_color=FlareColors.VOID_MEDIUM,
            corner_radius=16,
            glow_color=FlareColors.FIRE_TANGERINE
        )
        section.pack(fill="x", padx=30, pady=(0, 12))

        # Header
        header = ctk.CTkFrame(section, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(20, 16))

        icon_label = ctk.CTkLabel(header, text="🔧", font=ctk.CTkFont(size=16))
        icon_label.pack(side="left", padx=(0, 8))

        title = ctk.CTkLabel(
            header,
            text="ADVANCED OPTIONS",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=FlareColors.FIRE_TANGERINE
        )
        title.pack(side="left")

        # Checkboxes
        checks_frame = ctk.CTkFrame(section, fg_color="transparent")
        checks_frame.pack(fill="x", padx=24, pady=(0, 20))

        # Row 1
        row1 = ctk.CTkFrame(checks_frame, fg_color="transparent")
        row1.pack(fill="x", pady=(0, 10))

        self.sub_check = ctk.CTkCheckBox(
            row1,
            text="Download Subtitles",
            variable=self.download_subtitles,
            font=ctk.CTkFont(size=12),
            fg_color=FlareColors.FIRE_FLAME,
            hover_color=FlareColors.FIRE_ORANGE,
            border_color=FlareColors.VOID_BORDER,
            checkmark_color=FlareColors.VOID_DEEP
        )
        self.sub_check.pack(side="left", padx=(0, 30))

        self.thumb_check = ctk.CTkCheckBox(
            row1,
            text="Download Thumbnail",
            variable=self.download_thumbnail,
            font=ctk.CTkFont(size=12),
            fg_color=FlareColors.FIRE_FLAME,
            hover_color=FlareColors.FIRE_ORANGE,
            border_color=FlareColors.VOID_BORDER,
            checkmark_color=FlareColors.VOID_DEEP
        )
        self.thumb_check.pack(side="left", padx=(0, 30))

        self.meta_check = ctk.CTkCheckBox(
            row1,
            text="Embed Metadata",
            variable=self.embed_metadata,
            font=ctk.CTkFont(size=12),
            fg_color=FlareColors.FIRE_FLAME,
            hover_color=FlareColors.FIRE_ORANGE,
            border_color=FlareColors.VOID_BORDER,
            checkmark_color=FlareColors.VOID_DEEP
        )
        self.meta_check.pack(side="left")

    def _create_action_section(self):
        """Create download and cancel buttons"""
        section = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        section.pack(fill="x", padx=30, pady=(0, 12))

        # Download button - large and prominent
        self.download_btn = AnimatedButton(
            section,
            text="🔥  DOWNLOAD",
            command=self._start_download,
            height=60,
            corner_radius=14,
            font=ctk.CTkFont(size=18, weight="bold"),
            fg_color=FlareColors.FIRE_FLAME,
            hover_color=FlareColors.FIRE_ORANGE,
            text_color=FlareColors.TEXT_PRIMARY,
            glow_color=FlareColors.FIRE_GOLD
        )
        self.download_btn.pack(side="left", fill="x", expand=True, padx=(0, 12))

        # Cancel button
        self.cancel_btn = AnimatedButton(
            section,
            text="✕",
            command=self._cancel_download,
            width=60,
            height=60,
            corner_radius=14,
            font=ctk.CTkFont(size=20, weight="bold"),
            fg_color=FlareColors.VOID_LIGHT,
            hover_color=FlareColors.ERROR,
            text_color=FlareColors.TEXT_MUTED,
            state="disabled",
            glow_color=FlareColors.ERROR
        )
        self.cancel_btn.pack(side="right")

    def _create_progress_section(self):
        """Create progress display"""
        section = GlowFrame(
            self.scroll_frame,
            fg_color=FlareColors.VOID_MEDIUM,
            corner_radius=16,
            glow_color=FlareColors.FIRE_FLAME
        )
        section.pack(fill="x", padx=30, pady=(0, 12))

        # Status row
        status_row = ctk.CTkFrame(section, fg_color="transparent")
        status_row.pack(fill="x", padx=24, pady=(20, 10))

        self.status_label = ctk.CTkLabel(
            status_row,
            text="Ready to download",
            font=ctk.CTkFont(size=13),
            text_color=FlareColors.TEXT_SECONDARY
        )
        self.status_label.pack(side="left")

        self.speed_label = ctk.CTkLabel(
            status_row,
            text="",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=FlareColors.FIRE_GOLD
        )
        self.speed_label.pack(side="right")

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(
            section,
            height=12,
            corner_radius=6,
            progress_color=FlareColors.FIRE_FLAME,
            fg_color=FlareColors.VOID_DARK,
            border_width=0
        )
        self.progress_bar.pack(fill="x", padx=24, pady=(0, 8))
        self.progress_bar.set(0)

        # Info row
        info_row = ctk.CTkFrame(section, fg_color="transparent")
        info_row.pack(fill="x", padx=24, pady=(0, 20))

        self.progress_label = ctk.CTkLabel(
            info_row,
            text="0%",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=FlareColors.FIRE_FLAME
        )
        self.progress_label.pack(side="left")

        self.eta_label = ctk.CTkLabel(
            info_row,
            text="",
            font=ctk.CTkFont(size=11),
            text_color=FlareColors.TEXT_MUTED
        )
        self.eta_label.pack(side="right")

    def _create_log_section(self):
        """Create log display"""
        section = GlowFrame(
            self.scroll_frame,
            fg_color=FlareColors.VOID_MEDIUM,
            corner_radius=16,
            glow_color=FlareColors.VOID_BORDER
        )
        section.pack(fill="both", expand=True, padx=30, pady=(0, 12))

        # Header
        header = ctk.CTkFrame(section, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(20, 12))

        icon_label = ctk.CTkLabel(header, text="📋", font=ctk.CTkFont(size=16))
        icon_label.pack(side="left", padx=(0, 8))

        title = ctk.CTkLabel(
            header,
            text="ACTIVITY LOG",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=FlareColors.TEXT_SECONDARY
        )
        title.pack(side="left")

        clear_btn = AnimatedButton(
            header,
            text="Clear",
            command=self._clear_log,
            width=60,
            height=28,
            corner_radius=6,
            fg_color="transparent",
            text_color=FlareColors.TEXT_MUTED,
            hover_color=FlareColors.VOID_HOVER,
            font=ctk.CTkFont(size=10),
            glow_color=FlareColors.FIRE_ORANGE
        )
        clear_btn.pack(side="right")

        # Log text
        self.log_text = ctk.CTkTextbox(
            section,
            height=120,
            corner_radius=12,
            fg_color=FlareColors.VOID_DARK,
            text_color=FlareColors.TEXT_SECONDARY,
            font=ctk.CTkFont(family="Consolas", size=11),
            border_width=1,
            border_color=FlareColors.VOID_BORDER
        )
        self.log_text.pack(fill="both", expand=True, padx=24, pady=(0, 20))

    def _create_footer(self):
        """Create footer"""
        footer = ctk.CTkFrame(self.scroll_frame, fg_color=FlareColors.VOID_DARK, height=40, corner_radius=0)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)

        footer_text = ctk.CTkLabel(
            footer,
            text=f"Flare Download v{__version__}  •  Part of the Flare ecosystem  •  Powered by yt-dlp",
            font=ctk.CTkFont(size=10),
            text_color=FlareColors.TEXT_MUTED
        )
        footer_text.pack(expand=True)

    # Animation methods
    def _animate_title(self):
        """Animate fire colors on title"""
        self.fire_index = (self.fire_index + 1) % len(self.fire_colors)
        self.title_flare.configure(text_color=self.fire_colors[self.fire_index])
        self.after(400, self._animate_title)

    # Event handlers
    def _on_type_change(self, value):
        """Handle media type toggle"""
        if value == "Audio":
            self.format_menu.configure(values=self.audio_formats)
            self.format_var.set("mp3")
            self.quality_label.configure(text="BITRATE")
            self.quality_menu.pack_forget()
            self.audio_quality_menu.pack(fill="x")
        else:
            self.format_menu.configure(values=self.video_formats)
            self.format_var.set("mp4")
            self.quality_label.configure(text="QUALITY")
            self.audio_quality_menu.pack_forget()
            self.quality_menu.pack(fill="x")

    def _paste_url(self):
        """Paste URL from clipboard"""
        try:
            clipboard = self.clipboard_get()
            self.url_entry.delete(0, "end")
            self.url_entry.insert(0, clipboard)
            self._log("URL pasted from clipboard", "info")
        except Exception:
            self._log("Failed to paste from clipboard", "error")

    def _clear_url(self):
        """Clear URL entry"""
        self.url_entry.delete(0, "end")

    def _clear_log(self):
        """Clear log"""
        self.log_text.delete("1.0", "end")

    def _browse_path(self):
        """Browse for save location"""
        path = filedialog.askdirectory(initialdir=self.download_path.get())
        if path:
            self.download_path.set(path)
            self._log(f"Save location: {path}", "info")

    def _log(self, message, msg_type="info"):
        """Add message to log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        icons = {"info": "•", "success": "✓", "error": "✗", "warning": "⚠"}
        icon = icons.get(msg_type, "•")
        self.log_text.insert("end", f"[{timestamp}] {icon} {message}\n")
        self.log_text.see("end")

    def _update_progress(self, progress, status="Downloading...", speed="", eta=""):
        """Update progress UI"""
        self.progress_bar.set(progress / 100)
        self.progress_label.configure(text=f"{progress:.1f}%")
        self.status_label.configure(text=status)
        self.speed_label.configure(text=speed)
        self.eta_label.configure(text=eta)

    def _fetch_info(self):
        """Fetch video information"""
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Warning", "Please enter a URL first")
            return

        self._log("Fetching video info...", "info")

        def fetch():
            try:
                cmd = ["yt-dlp", "-j", "--no-download", url]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

                if result.returncode == 0:
                    info = json.loads(result.stdout)
                    title = info.get("title", "Unknown")
                    duration = info.get("duration", 0)
                    uploader = info.get("uploader", "Unknown")

                    if duration:
                        mins, secs = divmod(int(duration), 60)
                        hours, mins = divmod(mins, 60)
                        duration_str = f"{hours:02d}:{mins:02d}:{secs:02d}" if hours else f"{mins:02d}:{secs:02d}"
                    else:
                        duration_str = "Unknown"

                    self.after(0, lambda: self._log(f"Title: {title}", "success"))
                    self.after(0, lambda: self._log(f"Duration: {duration_str} | By: {uploader}", "info"))
                else:
                    error = result.stderr[:100] if result.stderr else "Unknown error"
                    self.after(0, lambda: self._log(f"Failed: {error}", "error"))

            except subprocess.TimeoutExpired:
                self.after(0, lambda: self._log("Request timed out", "error"))
            except FileNotFoundError:
                self.after(0, lambda: self._log("yt-dlp not found. Install with: pip install yt-dlp", "error"))
            except Exception as e:
                self.after(0, lambda: self._log(f"Error: {str(e)[:50]}", "error"))

        threading.Thread(target=fetch, daemon=True).start()

    def _check_updates(self):
        """Check for updates"""
        self._log("Checking for updates...", "info")

        def check():
            try:
                from updater import Updater
                updater = Updater()
                has_update, version, notes = updater.check_for_updates()
                if has_update:
                    self.after(0, lambda: self._show_update_dialog(version))
                else:
                    self.after(0, lambda: self._log(f"You're on the latest version (v{__version__})", "success"))
            except ImportError:
                self.after(0, lambda: self._log("Update module not available", "warning"))
            except Exception as e:
                self.after(0, lambda: self._log(f"Update check failed: {str(e)[:30]}", "error"))

        threading.Thread(target=check, daemon=True).start()

    def _show_update_dialog(self, version):
        """Show update dialog"""
        if messagebox.askyesno("Update Available",
            f"Flare Download v{version} is available!\n\nCurrent: v{__version__}\n\nOpen download page?"):
            import webbrowser
            webbrowser.open("https://github.com/contactmukundthiru-cyber/Multi-Platform-Downloader/releases/latest")

    def _start_download(self):
        """Start download"""
        url = self.url_entry.get().strip()

        if not url:
            messagebox.showerror("Error", "Please enter a video URL")
            return

        if self.is_downloading:
            messagebox.showwarning("Warning", "Download already in progress")
            return

        # Basic URL validation
        if not re.match(r'^https?://[^\s/$.?#].[^\s]*$', url):
            messagebox.showerror("Error", "Please enter a valid URL")
            return

        # Check output path
        if not os.path.isdir(self.download_path.get()):
            messagebox.showerror("Error", f"Output directory does not exist")
            return

        self.is_downloading = True
        self.download_btn.configure(state="disabled", text="⏳  DOWNLOADING...")
        self.cancel_btn.configure(state="normal", text_color=FlareColors.TEXT_PRIMARY)
        self._update_progress(0, "Preparing download...")

        thread = threading.Thread(target=self._download, args=(url,), daemon=True)
        thread.start()

    def _cancel_download(self):
        """Cancel download"""
        if self.current_process:
            self.current_process.terminate()
            self._log("Download cancelled", "warning")
            self._download_complete(False, "Cancelled by user")

    def _download(self, url):
        """Download video/audio"""
        try:
            self.after(0, lambda: self._log(f"Starting: {url[:50]}...", "info"))

            output_path = self.download_path.get()
            output_template = os.path.join(output_path, "%(title)s.%(ext)s")
            format_choice = self.format_var.get()

            # Build command
            cmd = ["yt-dlp", "--newline", "--progress", "--no-warnings"]

            if format_choice in self.audio_formats:
                # Audio download
                bitrate = self.audio_quality_var.get().split()[0]
                cmd.extend(["-x", "--audio-format", format_choice])
                cmd.extend(["--audio-quality", f"{bitrate}K"])
                self.after(0, lambda: self._log(f"Audio: {format_choice.upper()} @ {bitrate}kbps", "info"))
            else:
                # Video download
                quality = self.quality_var.get()

                if "Best" in quality:
                    cmd.extend(["-f", "bestvideo+bestaudio/best"])
                else:
                    # Extract resolution
                    match = re.search(r'(\d+)p', quality)
                    if match:
                        height = match.group(1)
                        cmd.extend(["-f", f"bestvideo[height<={height}]+bestaudio/best[height<={height}]/best"])
                    else:
                        cmd.extend(["-f", "bestvideo+bestaudio/best"])

                cmd.extend(["--merge-output-format", format_choice])
                self.after(0, lambda: self._log(f"Video: {format_choice.upper()} @ {quality}", "info"))

            # Advanced options
            if self.download_subtitles.get():
                cmd.extend(["--write-subs", "--sub-lang", "en"])

            if self.download_thumbnail.get():
                cmd.append("--write-thumbnail")

            if self.embed_metadata.get():
                cmd.append("--embed-metadata")

            cmd.extend(["-o", output_template, url])

            # Execute
            self.current_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )

            for line in self.current_process.stdout:
                line = line.strip()
                if not line:
                    continue

                # Parse progress
                progress_match = re.search(r'(\d+\.?\d*)%', line)
                speed_match = re.search(r'at\s+([\d.]+\s*\w+/s)', line)
                eta_match = re.search(r'ETA\s+([\d:]+)', line)

                if progress_match:
                    progress = float(progress_match.group(1))
                    speed = speed_match.group(1) if speed_match else ""
                    eta = f"ETA: {eta_match.group(1)}" if eta_match else ""
                    self.after(0, lambda p=progress, s=speed, e=eta: self._update_progress(p, "Downloading...", s, e))

                # Log important messages
                if any(x in line.lower() for x in ["destination", "merger", "extract", "download"]):
                    display = line[:80] + "..." if len(line) > 80 else line
                    self.after(0, lambda l=display: self._log(l, "info"))

            self.current_process.wait()

            if self.current_process.returncode == 0:
                self.after(0, lambda: self._download_complete(True))
            else:
                self.after(0, lambda: self._download_complete(False, "Download failed"))

        except FileNotFoundError:
            self.after(0, lambda: self._download_complete(False, "yt-dlp not found"))
        except Exception as e:
            self.after(0, lambda: self._download_complete(False, str(e)[:50]))
        finally:
            self.current_process = None

    def _download_complete(self, success, error=None):
        """Handle download completion"""
        self.is_downloading = False
        self.download_btn.configure(state="normal", text="🔥  DOWNLOAD")
        self.cancel_btn.configure(state="disabled", text_color=FlareColors.TEXT_MUTED)

        if success:
            self._update_progress(100, "Download complete!", "", "")
            self._log("Download completed successfully!", "success")
            self.progress_bar.configure(progress_color=FlareColors.SUCCESS)
        else:
            self._update_progress(0, "Download failed", "", "")
            self._log(f"Failed: {error}", "error")
            self.progress_bar.configure(progress_color=FlareColors.ERROR)

        # Reset color after delay
        self.after(3000, lambda: self.progress_bar.configure(progress_color=FlareColors.FIRE_FLAME))

    def _on_closing(self):
        """Handle window close"""
        if self.is_downloading:
            if messagebox.askyesno("Confirm Exit", "Download in progress. Cancel and exit?"):
                if self.current_process:
                    self.current_process.terminate()
                self.destroy()
        else:
            self.destroy()


def main():
    app = FlareDownloader()
    app.mainloop()


if __name__ == "__main__":
    main()
