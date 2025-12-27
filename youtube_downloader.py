#!/usr/bin/env python3
"""
███████╗██╗      █████╗ ██████╗ ███████╗
██╔════╝██║     ██╔══██╗██╔══██╗██╔════╝
█████╗  ██║     ███████║██████╔╝█████╗
██╔══╝  ██║     ██╔══██║██╔══██╗██╔══╝
██║     ███████╗██║  ██║██║  ██║███████╗
╚═╝     ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝

FLARE DOWNLOAD - Premium Multi-Platform Video Downloader
Part of the Flare ecosystem

Design Philosophy: Minimal. Bold. Cinematic.
"""

import sys
import os

# =============================================================================
# DEPENDENCY CHECK - Show helpful errors before anything else
# =============================================================================
def check_dependencies():
    """Check all required dependencies and show helpful messages."""
    errors = []

    # Check tkinter
    try:
        import tkinter
    except ImportError:
        errors.append(
            "tkinter is not installed.\n"
            "  Install with:\n"
            "    Ubuntu/Debian: sudo apt install python3-tk\n"
            "    Fedora: sudo dnf install python3-tkinter\n"
            "    macOS: brew install python-tk\n"
            "    Windows: Reinstall Python with 'tcl/tk' option checked"
        )

    # Check customtkinter
    try:
        import customtkinter
    except ImportError:
        errors.append(
            "customtkinter is not installed.\n"
            "  Install with: pip install customtkinter"
        )

    if errors:
        print("\n" + "=" * 60)
        print("FLARE DOWNLOAD - Missing Dependencies")
        print("=" * 60)
        for i, err in enumerate(errors, 1):
            print(f"\n[{i}] {err}")
        print("\n" + "=" * 60)
        print("After installing dependencies, run again:")
        print(f"  python3 {sys.argv[0]}")
        print("=" * 60 + "\n")
        sys.exit(1)

check_dependencies()

# Now safe to import
import customtkinter as ctk
from tkinter import filedialog, messagebox, Canvas
import threading
import re
import subprocess
import math
import random
from datetime import datetime
from typing import Optional, List

try:
    from version import __version__
except ImportError:
    __version__ = "2.6.0"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


# =============================================================================
# FLARE DESIGN SYSTEM
# Minimal. Bold. Cinematic.
# =============================================================================
class Flare:
    """Design tokens matching flare.mukundthiru.com"""
    # Void - Pure darkness
    BLACK = "#000000"
    VOID = "#030303"

    # Surfaces - Subtle elevation
    SURFACE_1 = "#0a0a0a"
    SURFACE_2 = "#0f0f0f"
    SURFACE_3 = "#141414"

    # Borders
    BORDER = "#1a1a1a"
    BORDER_HOVER = "#252525"

    # Fire palette - THE soul of Flare
    FIRE_BLOOD = "#8b0000"
    FIRE_CRIMSON = "#dc143c"
    FIRE = "#ff4500"         # Primary
    FIRE_BRIGHT = "#ff6b35"
    FIRE_ORANGE = "#ff8c00"
    FIRE_AMBER = "#ffa500"
    FIRE_GOLD = "#ffc107"

    # Text
    WHITE = "#ffffff"
    WHITE_DIM = "#e5e5e5"
    GRAY = "#888888"
    GRAY_DIM = "#555555"
    GRAY_DARK = "#333333"

    # Status
    SUCCESS = "#00ff88"
    ERROR = "#ff3366"
    WARNING = "#ffaa00"


# =============================================================================
# ANIMATED EMBER PARTICLES
# =============================================================================
class EmberCanvas(Canvas):
    """Floating ember particles for cinematic effect."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=Flare.BLACK, highlightthickness=0, **kwargs)
        self.embers: List[dict] = []
        self.running = True
        self._create_embers(20)
        self._animate()

    def _create_embers(self, count):
        for _ in range(count):
            self.embers.append({
                'x': random.randint(0, 800),
                'y': random.randint(0, 900),
                'size': random.uniform(1, 3),
                'speed': random.uniform(0.3, 1.2),
                'opacity': random.uniform(0.2, 0.7),
                'drift': random.uniform(-0.3, 0.3),
                'flicker': random.uniform(0, math.pi * 2)
            })

    def _animate(self):
        if not self.running:
            return

        self.delete("ember")
        w = self.winfo_width() or 800
        h = self.winfo_height() or 900

        for e in self.embers:
            # Float upward
            e['y'] -= e['speed']
            e['x'] += e['drift'] + math.sin(e['flicker']) * 0.2
            e['flicker'] += 0.05

            # Reset if off screen
            if e['y'] < -10:
                e['y'] = h + 10
                e['x'] = random.randint(0, w)
            if e['x'] < -10:
                e['x'] = w + 10
            elif e['x'] > w + 10:
                e['x'] = -10

            # Flicker effect
            flicker = 0.5 + 0.5 * math.sin(e['flicker'])
            alpha = int(e['opacity'] * flicker * 255)

            # Color gradient from red to orange
            r = min(255, 200 + int(55 * flicker))
            g = min(255, 50 + int(80 * flicker))
            b = 0
            color = f'#{r:02x}{g:02x}{b:02x}'

            # Draw ember
            s = e['size'] * (0.8 + 0.4 * flicker)
            self.create_oval(
                e['x'] - s, e['y'] - s,
                e['x'] + s, e['y'] + s,
                fill=color, outline="", tags="ember"
            )

        self.after(33, self._animate)  # ~30 FPS

    def stop(self):
        self.running = False


# =============================================================================
# ANIMATED GLOW BUTTON
# =============================================================================
class FlareButton(ctk.CTkButton):
    """Button with pulsing glow animation."""

    def __init__(self, master, glow=False, **kwargs):
        self.glow = glow
        self.glow_phase = 0
        self.original_fg = kwargs.get('fg_color', Flare.FIRE)

        super().__init__(master, **kwargs)

        if glow:
            self._animate_glow()

    def _animate_glow(self):
        if not self.glow or not self.winfo_exists():
            return

        self.glow_phase += 0.08
        intensity = 0.85 + 0.15 * math.sin(self.glow_phase)

        # Interpolate color
        base = int(0xff * intensity)
        color = f'#{base:02x}{int(0x45 * intensity):02x}00'

        try:
            self.configure(fg_color=color)
        except:
            pass

        self.after(50, self._animate_glow)


# =============================================================================
# ANIMATED PROGRESS RING
# =============================================================================
class ProgressRing(Canvas):
    """Circular progress indicator with fire gradient."""

    def __init__(self, parent, size=60, thickness=4, **kwargs):
        super().__init__(parent, width=size, height=size,
                        bg=Flare.BLACK, highlightthickness=0, **kwargs)
        self.size = size
        self.thickness = thickness
        self.progress = 0
        self.rotation = 0
        self.active = False
        self._draw()

    def _draw(self):
        self.delete("all")
        pad = self.thickness + 2

        # Background ring
        self.create_arc(
            pad, pad, self.size - pad, self.size - pad,
            start=0, extent=360, style="arc",
            outline=Flare.SURFACE_2, width=self.thickness
        )

        if self.active or self.progress > 0:
            # Progress arc
            extent = self.progress * 3.6 if self.progress > 0 else 90
            start = self.rotation if self.active and self.progress == 0 else 90

            self.create_arc(
                pad, pad, self.size - pad, self.size - pad,
                start=start, extent=-extent, style="arc",
                outline=Flare.FIRE, width=self.thickness
            )

    def set_progress(self, value):
        self.progress = max(0, min(100, value))
        self._draw()

    def start_indeterminate(self):
        self.active = True
        self._spin()

    def stop(self):
        self.active = False
        self._draw()

    def _spin(self):
        if not self.active:
            return
        self.rotation = (self.rotation + 8) % 360
        self._draw()
        self.after(30, self._spin)


# =============================================================================
# MAIN APPLICATION
# =============================================================================
class FlareDownloadApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window setup
        self.title("FLARE DOWNLOAD")
        self.geometry("920x1000")
        self.minsize(800, 900)
        self.configure(fg_color=Flare.BLACK)

        # State
        self.is_downloading = False
        self.process: Optional[subprocess.Popen] = None

        # Variables
        self.url_var = ctk.StringVar()
        self.output_dir = ctk.StringVar(value=self._get_default_download_dir())
        self.format_var = ctk.StringVar(value="mp4")
        self.quality_var = ctk.StringVar(value="Best")
        self.media_type = ctk.StringVar(value="Video")

        # Format options
        self.video_formats = ["mp4", "webm", "mkv", "mov", "avi"]
        self.audio_formats = ["mp3", "m4a", "wav", "flac", "opus", "aac"]
        self.video_qualities = ["Best", "4K", "1080p", "720p", "480p", "360p"]
        self.audio_qualities = ["Best", "320k", "256k", "192k", "128k", "96k"]

        # Build UI
        self._build_ui()

        # Bind events
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.bind("<Configure>", self._on_resize)

        # Start fade-in animation
        self.attributes('-alpha', 0)
        self._fade_in()

    def _get_default_download_dir(self) -> str:
        """Get a valid default download directory."""
        candidates = [
            os.path.expanduser("~/Downloads"),
            os.path.expanduser("~/Desktop"),
            os.path.expanduser("~"),
            os.getcwd()
        ]
        for path in candidates:
            if os.path.isdir(path):
                return path
        return os.getcwd()

    def _fade_in(self, alpha=0):
        """Cinematic fade-in effect."""
        if alpha < 1:
            self.attributes('-alpha', alpha)
            self.after(20, lambda: self._fade_in(alpha + 0.05))
        else:
            self.attributes('-alpha', 1)

    def _on_resize(self, event=None):
        """Handle window resize."""
        pass

    # =========================================================================
    # UI BUILDING
    # =========================================================================
    def _build_ui(self):
        # Main container with ember background
        self.main_frame = ctk.CTkFrame(self, fg_color=Flare.BLACK)
        self.main_frame.pack(fill="both", expand=True)

        # Ember canvas (background)
        self.ember_canvas = EmberCanvas(self.main_frame)
        self.ember_canvas.place(relwidth=1, relheight=1)

        # Content overlay
        content = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=50, pady=50)

        self._build_header(content)
        self._build_url_section(content)
        self._build_options(content)
        self._build_output_section(content)
        self._build_action_section(content)
        self._build_progress_section(content)
        self._build_log_section(content)
        self._build_footer(content)

    def _build_header(self, parent):
        """Hero header with large title."""
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(fill="x", pady=(0, 50))

        # Title container
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(anchor="w")

        # FLARE - Large display font
        title = ctk.CTkLabel(
            title_frame,
            text="FLARE",
            font=ctk.CTkFont(family="Arial Black", size=72, weight="bold"),
            text_color=Flare.WHITE
        )
        title.pack(side="left")

        # Animated fire accent dot
        dot_frame = ctk.CTkFrame(title_frame, fg_color="transparent", width=20, height=72)
        dot_frame.pack(side="left", padx=(15, 15))
        dot_frame.pack_propagate(False)

        self.fire_dot = ctk.CTkFrame(
            dot_frame,
            fg_color=Flare.FIRE,
            width=12, height=12,
            corner_radius=6
        )
        self.fire_dot.place(relx=0.5, rely=0.5, anchor="center")
        self._animate_fire_dot()

        # DOWNLOAD subtitle
        subtitle = ctk.CTkLabel(
            title_frame,
            text="DOWNLOAD",
            font=ctk.CTkFont(family="Arial", size=16, weight="bold"),
            text_color=Flare.GRAY
        )
        subtitle.pack(side="left", pady=(30, 0))

        # Version badge
        version_frame = ctk.CTkFrame(header, fg_color=Flare.SURFACE_1, corner_radius=4)
        version_frame.pack(anchor="e", pady=(10, 0))

        ctk.CTkLabel(
            version_frame,
            text=f"  v{__version__}  ",
            font=ctk.CTkFont(family="Consolas", size=11),
            text_color=Flare.GRAY_DIM
        ).pack(padx=8, pady=4)

        # Tagline
        ctk.CTkLabel(
            header,
            text="Download from YouTube, TikTok, Instagram, Twitter & 1000+ sites",
            font=ctk.CTkFont(size=13),
            text_color=Flare.GRAY
        ).pack(anchor="w", pady=(20, 0))

    def _animate_fire_dot(self):
        """Pulsing fire dot animation."""
        if not hasattr(self, 'fire_dot') or not self.fire_dot.winfo_exists():
            return

        if not hasattr(self, '_dot_phase'):
            self._dot_phase = 0

        self._dot_phase += 0.1
        scale = 1 + 0.3 * math.sin(self._dot_phase)
        size = int(12 * scale)

        colors = [Flare.FIRE_CRIMSON, Flare.FIRE, Flare.FIRE_BRIGHT, Flare.FIRE_ORANGE]
        color_idx = int((self._dot_phase / 0.5) % len(colors))

        try:
            self.fire_dot.configure(
                width=size, height=size,
                corner_radius=size // 2,
                fg_color=colors[color_idx]
            )
        except:
            pass

        self.after(50, self._animate_fire_dot)

    def _build_url_section(self, parent):
        """URL input with corner accents."""
        section = ctk.CTkFrame(parent, fg_color="transparent")
        section.pack(fill="x", pady=(0, 30))

        # Label
        label_frame = ctk.CTkFrame(section, fg_color="transparent")
        label_frame.pack(fill="x", pady=(0, 12))

        # Fire bar accent
        ctk.CTkFrame(
            label_frame, fg_color=Flare.FIRE,
            width=3, height=14, corner_radius=0
        ).pack(side="left", padx=(0, 10))

        ctk.CTkLabel(
            label_frame,
            text="VIDEO URL",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=Flare.WHITE_DIM
        ).pack(side="left")

        # Input container with corner accents
        input_container = ctk.CTkFrame(section, fg_color="transparent")
        input_container.pack(fill="x")

        # The actual input
        self.url_entry = ctk.CTkEntry(
            input_container,
            textvariable=self.url_var,
            placeholder_text="Paste video URL here...",
            height=60,
            corner_radius=0,
            border_width=2,
            border_color=Flare.BORDER,
            fg_color=Flare.SURFACE_1,
            text_color=Flare.WHITE,
            placeholder_text_color=Flare.GRAY_DIM,
            font=ctk.CTkFont(size=15)
        )
        self.url_entry.pack(fill="x")

        # Corner accents overlay
        self._add_corner_accents(input_container)

        # Focus effects
        self.url_entry.bind("<FocusIn>", lambda e: self._on_url_focus(True))
        self.url_entry.bind("<FocusOut>", lambda e: self._on_url_focus(False))

        # Action buttons
        btn_frame = ctk.CTkFrame(section, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(15, 0))

        for text, cmd in [("PASTE", self._paste_url), ("CLEAR", self._clear_url)]:
            btn = ctk.CTkButton(
                btn_frame, text=text, command=cmd,
                width=80, height=32, corner_radius=0,
                fg_color="transparent",
                hover_color=Flare.SURFACE_2,
                border_width=1, border_color=Flare.BORDER,
                text_color=Flare.GRAY,
                font=ctk.CTkFont(size=10, weight="bold")
            )
            btn.pack(side="left", padx=(0, 10))

    def _add_corner_accents(self, container):
        """Add L-shaped corner accents to container."""
        # Create overlay frame
        overlay = ctk.CTkFrame(container, fg_color="transparent")
        overlay.place(relwidth=1, relheight=1)

        accent_len = 16
        accent_thick = 2

        positions = [
            # Top-left
            {'x': 0, 'y': 0, 'w': accent_len, 'h': accent_thick},
            {'x': 0, 'y': 0, 'w': accent_thick, 'h': accent_len},
            # Top-right
            {'relx': 1, 'x': -accent_len, 'y': 0, 'w': accent_len, 'h': accent_thick},
            {'relx': 1, 'x': -accent_thick, 'y': 0, 'w': accent_thick, 'h': accent_len},
            # Bottom-left
            {'x': 0, 'rely': 1, 'y': -accent_thick, 'w': accent_len, 'h': accent_thick},
            {'x': 0, 'rely': 1, 'y': -accent_len, 'w': accent_thick, 'h': accent_len},
            # Bottom-right
            {'relx': 1, 'x': -accent_len, 'rely': 1, 'y': -accent_thick, 'w': accent_len, 'h': accent_thick},
            {'relx': 1, 'x': -accent_thick, 'rely': 1, 'y': -accent_len, 'w': accent_thick, 'h': accent_len},
        ]

        for pos in positions:
            f = ctk.CTkFrame(overlay, fg_color=Flare.FIRE, corner_radius=0)
            f.configure(width=pos.pop('w'), height=pos.pop('h'))
            f.place(**pos)

    def _on_url_focus(self, focused):
        """Handle URL input focus."""
        color = Flare.FIRE if focused else Flare.BORDER
        self.url_entry.configure(border_color=color)

    def _build_options(self, parent):
        """Type, Format, Quality options."""
        section = ctk.CTkFrame(parent, fg_color="transparent")
        section.pack(fill="x", pady=(0, 30))
        section.columnconfigure((0, 1, 2), weight=1, uniform="opt")

        # Type selector
        type_frame = self._build_option_group(section, "TYPE", 0)
        self.type_seg = ctk.CTkSegmentedButton(
            type_frame,
            values=["Video", "Audio"],
            variable=self.media_type,
            command=self._on_type_change,
            height=44,
            corner_radius=0,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=Flare.SURFACE_1,
            selected_color=Flare.FIRE,
            selected_hover_color=Flare.FIRE_BRIGHT,
            unselected_color=Flare.SURFACE_2,
            unselected_hover_color=Flare.SURFACE_3,
            text_color=Flare.WHITE
        )
        self.type_seg.pack(fill="x")

        # Format dropdown
        fmt_frame = self._build_option_group(section, "FORMAT", 1)
        self.fmt_menu = ctk.CTkOptionMenu(
            fmt_frame,
            values=self.video_formats,
            variable=self.format_var,
            height=44,
            corner_radius=0,
            fg_color=Flare.SURFACE_1,
            button_color=Flare.SURFACE_2,
            button_hover_color=Flare.SURFACE_3,
            dropdown_fg_color=Flare.SURFACE_1,
            dropdown_hover_color=Flare.FIRE,
            text_color=Flare.WHITE,
            font=ctk.CTkFont(size=13)
        )
        self.fmt_menu.pack(fill="x")

        # Quality dropdown
        qual_frame = self._build_option_group(section, "QUALITY", 2)
        self.qual_menu = ctk.CTkOptionMenu(
            qual_frame,
            values=self.video_qualities,
            variable=self.quality_var,
            height=44,
            corner_radius=0,
            fg_color=Flare.SURFACE_1,
            button_color=Flare.SURFACE_2,
            button_hover_color=Flare.SURFACE_3,
            dropdown_fg_color=Flare.SURFACE_1,
            dropdown_hover_color=Flare.FIRE,
            text_color=Flare.WHITE,
            font=ctk.CTkFont(size=13)
        )
        self.qual_menu.pack(fill="x")

    def _build_option_group(self, parent, label, col):
        """Build a labeled option group."""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        padx = (0, 12) if col == 0 else ((12, 0) if col == 2 else (6, 6))
        frame.grid(row=0, column=col, sticky="ew", padx=padx)

        # Label with accent
        label_frame = ctk.CTkFrame(frame, fg_color="transparent")
        label_frame.pack(fill="x", pady=(0, 8))

        ctk.CTkFrame(
            label_frame, fg_color=Flare.FIRE,
            width=2, height=10, corner_radius=0
        ).pack(side="left", padx=(0, 8))

        ctk.CTkLabel(
            label_frame,
            text=label,
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=Flare.GRAY
        ).pack(side="left")

        return frame

    def _build_output_section(self, parent):
        """Output directory selection."""
        section = ctk.CTkFrame(parent, fg_color="transparent")
        section.pack(fill="x", pady=(0, 35))

        # Label
        label_frame = ctk.CTkFrame(section, fg_color="transparent")
        label_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkFrame(
            label_frame, fg_color=Flare.FIRE,
            width=2, height=10, corner_radius=0
        ).pack(side="left", padx=(0, 8))

        ctk.CTkLabel(
            label_frame,
            text="SAVE TO",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=Flare.GRAY
        ).pack(side="left")

        # Path input row
        row = ctk.CTkFrame(section, fg_color="transparent")
        row.pack(fill="x")

        self.path_entry = ctk.CTkEntry(
            row,
            textvariable=self.output_dir,
            height=44,
            corner_radius=0,
            border_width=1,
            border_color=Flare.BORDER,
            fg_color=Flare.SURFACE_1,
            text_color=Flare.WHITE_DIM,
            font=ctk.CTkFont(size=12)
        )
        self.path_entry.pack(side="left", fill="x", expand=True, padx=(0, 12))

        ctk.CTkButton(
            row,
            text="BROWSE",
            command=self._browse_folder,
            width=100, height=44,
            corner_radius=0,
            fg_color=Flare.SURFACE_2,
            hover_color=Flare.SURFACE_3,
            text_color=Flare.WHITE_DIM,
            font=ctk.CTkFont(size=11, weight="bold")
        ).pack(side="right")

    def _build_action_section(self, parent):
        """Download and cancel buttons."""
        section = ctk.CTkFrame(parent, fg_color="transparent")
        section.pack(fill="x", pady=(0, 30))

        row = ctk.CTkFrame(section, fg_color="transparent")
        row.pack(fill="x")

        # DOWNLOAD - Primary CTA with glow
        self.download_btn = FlareButton(
            row,
            text="DOWNLOAD",
            command=self._start_download,
            height=60,
            corner_radius=0,
            fg_color=Flare.FIRE,
            hover_color=Flare.FIRE_BRIGHT,
            text_color=Flare.BLACK,
            font=ctk.CTkFont(size=16, weight="bold"),
            glow=True
        )
        self.download_btn.pack(side="left", fill="x", expand=True, padx=(0, 12))

        # CANCEL
        self.cancel_btn = ctk.CTkButton(
            row,
            text="CANCEL",
            command=self._cancel_download,
            width=100, height=60,
            corner_radius=0,
            fg_color=Flare.SURFACE_2,
            hover_color=Flare.ERROR,
            text_color=Flare.GRAY,
            font=ctk.CTkFont(size=12, weight="bold"),
            state="disabled"
        )
        self.cancel_btn.pack(side="right")

    def _build_progress_section(self, parent):
        """Progress display with ring and bar."""
        section = ctk.CTkFrame(parent, fg_color=Flare.SURFACE_1, corner_radius=0)
        section.pack(fill="x", pady=(0, 25))

        inner = ctk.CTkFrame(section, fg_color="transparent")
        inner.pack(fill="x", padx=25, pady=20)

        # Top row: status and speed
        top_row = ctk.CTkFrame(inner, fg_color="transparent")
        top_row.pack(fill="x", pady=(0, 12))

        # Progress ring
        self.progress_ring = ProgressRing(top_row, size=50, thickness=3)
        self.progress_ring.pack(side="left", padx=(0, 15))

        # Status text
        status_text = ctk.CTkFrame(top_row, fg_color="transparent")
        status_text.pack(side="left", fill="x", expand=True)

        self.status_label = ctk.CTkLabel(
            status_text,
            text="Ready to download",
            font=ctk.CTkFont(size=13),
            text_color=Flare.WHITE_DIM,
            anchor="w"
        )
        self.status_label.pack(anchor="w")

        self.detail_label = ctk.CTkLabel(
            status_text,
            text="Paste a URL and click Download",
            font=ctk.CTkFont(size=11),
            text_color=Flare.GRAY_DIM,
            anchor="w"
        )
        self.detail_label.pack(anchor="w", pady=(2, 0))

        # Speed and percent
        stats = ctk.CTkFrame(top_row, fg_color="transparent")
        stats.pack(side="right")

        self.speed_label = ctk.CTkLabel(
            stats,
            text="",
            font=ctk.CTkFont(family="Consolas", size=14),
            text_color=Flare.FIRE
        )
        self.speed_label.pack(anchor="e")

        self.percent_label = ctk.CTkLabel(
            stats,
            text="0%",
            font=ctk.CTkFont(family="Consolas", size=24, weight="bold"),
            text_color=Flare.WHITE
        )
        self.percent_label.pack(anchor="e")

        # Progress bar - thin and cinematic
        self.progress_bar = ctk.CTkProgressBar(
            inner,
            height=4,
            corner_radius=0,
            progress_color=Flare.FIRE,
            fg_color=Flare.SURFACE_3
        )
        self.progress_bar.pack(fill="x", pady=(8, 0))
        self.progress_bar.set(0)

    def _build_log_section(self, parent):
        """Collapsible log output."""
        section = ctk.CTkFrame(parent, fg_color="transparent")
        section.pack(fill="both", expand=True)

        # Header with toggle
        header = ctk.CTkFrame(section, fg_color="transparent")
        header.pack(fill="x", pady=(0, 8))

        ctk.CTkLabel(
            header,
            text="OUTPUT LOG",
            font=ctk.CTkFont(size=9, weight="bold"),
            text_color=Flare.GRAY_DIM
        ).pack(side="left")

        ctk.CTkButton(
            header,
            text="CLEAR",
            command=self._clear_log,
            width=50, height=22,
            corner_radius=0,
            fg_color="transparent",
            hover_color=Flare.SURFACE_2,
            text_color=Flare.GRAY_DIM,
            font=ctk.CTkFont(size=9)
        ).pack(side="right")

        # Log textbox
        self.log_text = ctk.CTkTextbox(
            section,
            height=120,
            corner_radius=0,
            fg_color=Flare.SURFACE_1,
            text_color=Flare.GRAY,
            font=ctk.CTkFont(family="Consolas", size=10),
            border_width=1,
            border_color=Flare.BORDER
        )
        self.log_text.pack(fill="both", expand=True)
        self._log("Flare Download initialized. Ready.")

    def _build_footer(self, parent):
        """Footer with branding."""
        footer = ctk.CTkFrame(parent, fg_color="transparent")
        footer.pack(fill="x", pady=(20, 0))

        # Fire accent line
        ctk.CTkFrame(
            footer, fg_color=Flare.FIRE,
            height=2, corner_radius=0
        ).pack(fill="x", pady=(0, 12))

        # Credits
        ctk.CTkLabel(
            footer,
            text="FLARE ECOSYSTEM  •  Powered by yt-dlp  •  Made by Mukund Thiru",
            font=ctk.CTkFont(size=10),
            text_color=Flare.GRAY_DIM
        ).pack()

    # =========================================================================
    # ACTIONS
    # =========================================================================
    def _paste_url(self):
        """Paste URL from clipboard."""
        try:
            url = self.clipboard_get()
            self.url_var.set(url)
            self._log("URL pasted from clipboard")
        except Exception:
            self._log("Clipboard is empty", error=True)

    def _clear_url(self):
        """Clear URL input."""
        self.url_var.set("")

    def _clear_log(self):
        """Clear log output."""
        self.log_text.delete("1.0", "end")

    def _browse_folder(self):
        """Browse for output folder."""
        folder = filedialog.askdirectory(initialdir=self.output_dir.get())
        if folder:
            self.output_dir.set(folder)
            self._log(f"Output folder: {folder}")

    def _on_type_change(self, value):
        """Handle media type change."""
        if value == "Audio":
            self.fmt_menu.configure(values=self.audio_formats)
            self.format_var.set("mp3")
            self.qual_menu.configure(values=self.audio_qualities)
            self.quality_var.set("Best")
        else:
            self.fmt_menu.configure(values=self.video_formats)
            self.format_var.set("mp4")
            self.qual_menu.configure(values=self.video_qualities)
            self.quality_var.set("Best")

    def _log(self, message, error=False):
        """Add message to log."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        icon = "✗" if error else "•"
        self.log_text.insert("end", f"{timestamp}  {icon}  {message}\n")
        self.log_text.see("end")

    def _update_progress(self, percent, status="", detail="", speed=""):
        """Update progress display."""
        self.progress_bar.set(percent / 100)
        self.progress_ring.set_progress(percent)
        self.percent_label.configure(text=f"{percent:.0f}%")

        if status:
            self.status_label.configure(text=status)
        if detail:
            self.detail_label.configure(text=detail)

        self.speed_label.configure(text=speed)

    def _set_downloading_state(self, downloading):
        """Update UI state for downloading."""
        self.is_downloading = downloading

        if downloading:
            self.download_btn.configure(
                state="disabled",
                fg_color=Flare.GRAY_DIM,
                text="DOWNLOADING..."
            )
            self.download_btn.glow = False
            self.cancel_btn.configure(state="normal", text_color=Flare.WHITE)
            self.progress_ring.start_indeterminate()
        else:
            self.download_btn.configure(
                state="normal",
                fg_color=Flare.FIRE,
                text="DOWNLOAD"
            )
            self.download_btn.glow = True
            self.download_btn._animate_glow()
            self.cancel_btn.configure(state="disabled", text_color=Flare.GRAY)
            self.progress_ring.stop()

    # =========================================================================
    # DOWNLOAD LOGIC
    # =========================================================================
    def _start_download(self):
        """Start the download process."""
        url = self.url_var.get().strip()

        # Validation
        if not url:
            messagebox.showerror("Error", "Please enter a video URL")
            return

        if not re.match(r'^https?://', url):
            messagebox.showerror("Error", "Please enter a valid URL starting with http:// or https://")
            return

        output_dir = self.output_dir.get()
        if not os.path.isdir(output_dir):
            try:
                os.makedirs(output_dir, exist_ok=True)
            except Exception as e:
                messagebox.showerror("Error", f"Cannot create output folder: {e}")
                return

        # Start download
        self._set_downloading_state(True)
        self._update_progress(0, "Starting download...", "Connecting to server...")
        self._log(f"Downloading: {url[:60]}...")

        threading.Thread(target=self._download_thread, args=(url,), daemon=True).start()

    def _cancel_download(self):
        """Cancel the current download."""
        if self.process:
            try:
                self.process.terminate()
            except:
                pass
            self._log("Download cancelled by user", error=True)
            self._finish_download(False, "Cancelled")

    def _download_thread(self, url):
        """Download thread - runs in background."""
        try:
            output_dir = self.output_dir.get()
            fmt = self.format_var.get()
            quality = self.quality_var.get()
            is_audio = self.media_type.get() == "Audio"

            # Output template
            template = os.path.join(output_dir, "%(title).100s.%(ext)s")

            # Find yt-dlp
            ytdlp = self._find_ytdlp()
            if not ytdlp:
                self.after(0, lambda: self._finish_download(False, "yt-dlp not found. Install with: pip install yt-dlp"))
                return

            # Build command
            cmd = [
                ytdlp,
                "--newline",
                "--progress",
                "--no-warnings",
                "--no-playlist",
                "--restrict-filenames",
                "--no-mtime"
            ]

            if is_audio:
                cmd.extend(["-x", "--audio-format", fmt])
                if quality != "Best":
                    bitrate = quality.replace("k", "")
                    cmd.extend(["--audio-quality", f"{bitrate}K"])
            else:
                if quality == "Best":
                    cmd.extend(["-f", "bestvideo+bestaudio/best"])
                elif quality == "4K":
                    cmd.extend(["-f", "bestvideo[height<=2160]+bestaudio/best[height<=2160]"])
                else:
                    height = quality.replace("p", "")
                    cmd.extend(["-f", f"bestvideo[height<={height}]+bestaudio/best[height<={height}]"])
                cmd.extend(["--merge-output-format", fmt])

            cmd.extend(["-o", template, url])

            # Environment with bundled tools
            env = self._get_env_with_tools()

            # Run process
            creation_flags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0

            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1,
                env=env,
                creationflags=creation_flags
            )

            # Parse output
            for line in self.process.stdout:
                line = line.strip()
                if not line:
                    continue

                # Parse progress
                match_pct = re.search(r'(\d+\.?\d*)%', line)
                match_speed = re.search(r'at\s+([\d.]+\s*\w+/s)', line)
                match_eta = re.search(r'ETA\s+(\d+:\d+)', line)

                if match_pct:
                    pct = float(match_pct.group(1))
                    speed = match_speed.group(1) if match_speed else ""
                    eta = f"ETA {match_eta.group(1)}" if match_eta else ""

                    self.after(0, lambda p=pct, s=speed, e=eta:
                        self._update_progress(p, "Downloading...", e, s))

                # Log interesting lines
                if "[download]" in line.lower() and "%" not in line:
                    self.after(0, lambda l=line: self._log(l[:80]))

            self.process.wait()
            success = self.process.returncode == 0
            self.after(0, lambda: self._finish_download(success))

        except FileNotFoundError:
            self.after(0, lambda: self._finish_download(False, "yt-dlp not found"))
        except Exception as e:
            self.after(0, lambda: self._finish_download(False, str(e)[:60]))
        finally:
            self.process = None

    def _find_ytdlp(self) -> Optional[str]:
        """Find yt-dlp executable."""
        # Check bundled location (Windows installer)
        if os.name == 'nt':
            base = os.path.dirname(os.path.abspath(__file__))
            bundled = os.path.join(base, "python", "Scripts", "yt-dlp.exe")
            if os.path.exists(bundled):
                return bundled

        # Check if in PATH
        try:
            result = subprocess.run(
                ["yt-dlp", "--version"],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                return "yt-dlp"
        except FileNotFoundError:
            pass

        return None

    def _get_env_with_tools(self) -> dict:
        """Get environment with bundled tools in PATH."""
        env = os.environ.copy()

        if os.name == 'nt':
            base = os.path.dirname(os.path.abspath(__file__))
            paths = [
                os.path.join(base, "python"),
                os.path.join(base, "python", "Scripts"),
                os.path.join(base, "ffmpeg"),
                os.path.join(base, "ffmpeg", "bin"),
                os.path.join(base, "node"),
            ]
            existing = [p for p in paths if os.path.isdir(p)]
            if existing:
                env["PATH"] = ";".join(existing) + ";" + env.get("PATH", "")

        return env

    def _finish_download(self, success, error=None):
        """Handle download completion."""
        self._set_downloading_state(False)

        if success:
            self._update_progress(100, "Download Complete!", "File saved to output folder", "")
            self._log("Download completed successfully!")
            self.progress_bar.configure(progress_color=Flare.SUCCESS)
            self.progress_ring.set_progress(100)

            # Flash success animation
            self._flash_success()
        else:
            msg = error or "Download failed"
            self._update_progress(0, "Download Failed", msg, "")
            self._log(f"Error: {msg}", error=True)
            self.progress_bar.configure(progress_color=Flare.ERROR)

        # Reset color after delay
        self.after(3000, lambda: self.progress_bar.configure(progress_color=Flare.FIRE))

    def _flash_success(self):
        """Flash success animation."""
        def flash(count=0):
            if count >= 6:
                self.progress_bar.configure(progress_color=Flare.SUCCESS)
                return
            color = Flare.WHITE if count % 2 == 0 else Flare.SUCCESS
            self.progress_bar.configure(progress_color=color)
            self.after(100, lambda: flash(count + 1))
        flash()

    def _on_close(self):
        """Handle window close."""
        if self.is_downloading:
            if messagebox.askyesno("Confirm Exit", "A download is in progress. Cancel and exit?"):
                if self.process:
                    try:
                        self.process.terminate()
                    except:
                        pass
                self.ember_canvas.stop()
                self.destroy()
        else:
            self.ember_canvas.stop()
            self.destroy()


# =============================================================================
# ENTRY POINT
# =============================================================================
def main():
    try:
        app = FlareDownloadApp()
        app.mainloop()
    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        print("\nIf the error persists, please report at:")
        print("https://github.com/contactmukundthiru-cyber/Multi-Platform-Downloader/issues")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
