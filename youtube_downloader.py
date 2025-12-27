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
from tkinter import filedialog, messagebox, Canvas, TclError
import threading
import re
import subprocess
import math
import random
from datetime import datetime
from typing import Optional, List

try:
    from version import __version__, GITHUB_REPO
except ImportError:
    __version__ = "2.6.1"
    GITHUB_REPO = "contactmukundthiru-cyber/Multi-Platform-Downloader"

# Import updater
try:
    from updater import Updater
    HAS_UPDATER = True
except ImportError:
    HAS_UPDATER = False

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
        self.frame_count = 0
        self._create_embers(25)  # More embers
        self._animate()

    def _create_embers(self, count):
        for _ in range(count):
            self.embers.append({
                'x': random.randint(0, 800),
                'y': random.randint(0, 900),
                'size': random.uniform(1.5, 4),  # Larger embers
                'speed': random.uniform(0.4, 1.5),  # Varied speeds
                'opacity': random.uniform(0.3, 0.9),  # More visible
                'drift': random.uniform(-0.5, 0.5),  # More drift
                'flicker': random.uniform(0, math.pi * 2),
                'pulse_speed': random.uniform(0.03, 0.08),  # Individual pulse speeds
                'color_offset': random.uniform(0, 1)  # Color variation
            })

    def _animate(self):
        if not self.running:
            return

        self.delete("ember")
        self.frame_count += 1
        w = self.winfo_width() or 800
        h = self.winfo_height() or 900

        for e in self.embers:
            # Float upward with smoother motion
            e['y'] -= e['speed']
            e['x'] += e['drift'] + math.sin(e['flicker']) * 0.3
            e['flicker'] += e['pulse_speed']

            # Reset if off screen
            if e['y'] < -10:
                e['y'] = h + 10
                e['x'] = random.randint(0, w)
                e['size'] = random.uniform(1.5, 4)
                e['speed'] = random.uniform(0.4, 1.5)
            if e['x'] < -10:
                e['x'] = w + 10
            elif e['x'] > w + 10:
                e['x'] = -10

            # Smoother flicker effect
            flicker = 0.5 + 0.5 * math.sin(e['flicker'])

            # Dynamic color based on ember state and color_offset
            hue_shift = e['color_offset'] + self.frame_count * 0.001
            r = min(255, int(180 + 75 * flicker))
            g = min(255, int(40 + 100 * flicker * (0.5 + 0.5 * math.sin(hue_shift))))
            b = min(60, int(20 * flicker))
            color = f'#{r:02x}{g:02x}{b:02x}'

            # Draw ember with glow effect (outer glow + inner core)
            s = e['size'] * (0.7 + 0.5 * flicker)

            # Outer glow (larger, dimmer)
            glow_s = s * 1.8
            glow_r = min(255, r // 2)
            glow_g = min(255, g // 3)
            glow_color = f'#{glow_r:02x}{glow_g:02x}00'
            self.create_oval(
                e['x'] - glow_s, e['y'] - glow_s,
                e['x'] + glow_s, e['y'] + glow_s,
                fill=glow_color, outline="", tags="ember"
            )

            # Inner core (brighter)
            self.create_oval(
                e['x'] - s, e['y'] - s,
                e['x'] + s, e['y'] + s,
                fill=color, outline="", tags="ember"
            )

        self.after(25, self._animate)  # ~40 FPS for smoother animation

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

        # Keyboard shortcuts
        self._setup_keyboard_shortcuts()

        # Drag and drop support
        self._setup_drag_drop()

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

    def _setup_keyboard_shortcuts(self):
        """Setup global keyboard shortcuts."""
        # Ctrl+V - Paste URL
        self.bind("<Control-v>", lambda e: self._paste_url())
        self.bind("<Control-V>", lambda e: self._paste_url())

        # Ctrl+L - Clear URL
        self.bind("<Control-l>", lambda e: self._clear_url())
        self.bind("<Control-L>", lambda e: self._clear_url())

        # Enter - Start download (when not in entry)
        self.bind("<Return>", self._on_enter_key)

        # Escape - Cancel download
        self.bind("<Escape>", lambda e: self._cancel_download() if self.is_downloading else None)

        # Ctrl+O - Browse folder
        self.bind("<Control-o>", lambda e: self._browse_folder())
        self.bind("<Control-O>", lambda e: self._browse_folder())

        # Log shortcuts on startup
        self._log("Shortcuts: Ctrl+V=Paste, Ctrl+L=Clear, Enter=Download, Esc=Cancel")

    def _on_enter_key(self, event=None):
        """Handle Enter key press."""
        # Don't trigger if typing in an entry
        focused = self.focus_get()
        if focused and hasattr(focused, '_entry'):
            return
        if not self.is_downloading and self.url_var.get().strip():
            self._start_download()

    def _setup_drag_drop(self):
        """Setup drag and drop support for URLs."""
        # Enable drag and drop on the main window
        try:
            # Try to use tkinterdnd2 if available
            self.drop_target_register('DND_Files', 'DND_Text')
            self.dnd_bind('<<Drop>>', self._on_drop)
        except:
            # Fallback: bind to standard events
            self.bind("<Button-1>", self._check_clipboard_on_focus)

        # Also make URL entry accept drops
        self.url_entry.bind("<Button-3>", self._show_context_menu)

    def _on_drop(self, event):
        """Handle drag and drop."""
        data = event.data
        if data:
            # Clean up the dropped data
            url = data.strip().strip('"').strip("'")
            if url.startswith(('http://', 'https://')):
                self.url_var.set(url)
                self._log("URL dropped")
                self._animate_url_drop()

    def _check_clipboard_on_focus(self, event=None):
        """Check clipboard when window gains focus (fallback for drag-drop)."""
        pass  # Placeholder for focus-based paste suggestion

    def _show_context_menu(self, event):
        """Show right-click context menu for URL entry."""
        menu = ctk.CTkFrame(self, fg_color=Flare.SURFACE_1, corner_radius=4)

        paste_btn = ctk.CTkButton(
            menu, text="Paste", command=lambda: [self._paste_url(), menu.destroy()],
            width=80, height=28, corner_radius=0,
            fg_color="transparent", hover_color=Flare.FIRE,
            text_color=Flare.WHITE, font=ctk.CTkFont(size=11)
        )
        paste_btn.pack(fill="x", padx=2, pady=2)

        clear_btn = ctk.CTkButton(
            menu, text="Clear", command=lambda: [self._clear_url(), menu.destroy()],
            width=80, height=28, corner_radius=0,
            fg_color="transparent", hover_color=Flare.FIRE,
            text_color=Flare.WHITE, font=ctk.CTkFont(size=11)
        )
        clear_btn.pack(fill="x", padx=2, pady=2)

        # Position menu at cursor
        menu.place(x=event.x_root - self.winfo_rootx(), y=event.y_root - self.winfo_rooty())

        # Close menu when clicking elsewhere
        def close_menu(e):
            if menu.winfo_exists():
                menu.destroy()
        self.bind("<Button-1>", close_menu, add="+")
        self.after(3000, lambda: menu.destroy() if menu.winfo_exists() else None)

    def _animate_url_drop(self):
        """Animate URL field when URL is dropped."""
        def flash(count=0):
            if count >= 4:
                self.url_entry.configure(border_color=Flare.BORDER)
                return
            color = Flare.SUCCESS if count % 2 == 0 else Flare.FIRE
            self.url_entry.configure(border_color=color)
            self.after(100, lambda: flash(count + 1))
        flash()

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
        header.pack(fill="x", pady=(0, 40))

        # Title row
        title_row = ctk.CTkFrame(header, fg_color="transparent")
        title_row.pack(anchor="w")

        # FLARE - Large display font with letter spacing effect
        title = ctk.CTkLabel(
            title_row,
            text="F L A R E",
            font=ctk.CTkFont(family="Arial Black", size=56, weight="bold"),
            text_color=Flare.WHITE
        )
        title.pack(side="left")

        # DOWNLOAD - Next to title
        subtitle = ctk.CTkLabel(
            title_row,
            text="D O W N L O A D",
            font=ctk.CTkFont(family="Arial", size=14, weight="bold"),
            text_color=Flare.FIRE
        )
        subtitle.pack(side="left", padx=(25, 0), pady=(20, 0))

        # Version badge - inline
        version_label = ctk.CTkLabel(
            title_row,
            text=f"v{__version__}",
            font=ctk.CTkFont(family="Consolas", size=10),
            text_color=Flare.GRAY_DIM
        )
        version_label.pack(side="left", padx=(15, 0), pady=(22, 0))

        # Tagline
        ctk.CTkLabel(
            header,
            text="YouTube  •  TikTok  •  Instagram  •  Twitter  •  1000+ sites",
            font=ctk.CTkFont(size=12),
            text_color=Flare.GRAY_DIM
        ).pack(anchor="w", pady=(15, 0))

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
        """URL input - prominent and clear."""
        section = ctk.CTkFrame(parent, fg_color="transparent")
        section.pack(fill="x", pady=(0, 25))

        # Label row
        label_row = ctk.CTkFrame(section, fg_color="transparent")
        label_row.pack(fill="x", pady=(0, 10))

        # Fire accent bar
        ctk.CTkFrame(
            label_row, fg_color=Flare.FIRE,
            width=4, height=16, corner_radius=0
        ).pack(side="left", padx=(0, 12))

        ctk.CTkLabel(
            label_row,
            text="PASTE VIDEO URL",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=Flare.WHITE
        ).pack(side="left")

        # URL Input Box - prominent with glow effect
        input_frame = ctk.CTkFrame(
            section,
            fg_color=Flare.SURFACE_2,
            corner_radius=8,
            border_width=2,
            border_color=Flare.FIRE_CRIMSON
        )
        input_frame.pack(fill="x", ipady=5)

        # The URL entry
        self.url_entry = ctk.CTkEntry(
            input_frame,
            textvariable=self.url_var,
            placeholder_text="https://youtube.com/watch?v=... or any video URL",
            height=50,
            corner_radius=6,
            border_width=0,
            fg_color=Flare.SURFACE_1,
            text_color=Flare.WHITE,
            placeholder_text_color=Flare.GRAY,
            font=ctk.CTkFont(size=14)
        )
        self.url_entry.pack(fill="x", padx=8, pady=8)

        # Focus effects
        self.url_entry.bind("<FocusIn>", lambda e: self._on_url_focus(True))
        self.url_entry.bind("<FocusOut>", lambda e: self._on_url_focus(False))

        # Allow Ctrl+V directly in the entry
        self.url_entry.bind("<Control-v>", self._paste_to_entry)
        self.url_entry.bind("<Control-V>", self._paste_to_entry)

        # Action buttons row
        btn_frame = ctk.CTkFrame(section, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(12, 0))

        # Paste button - more prominent
        paste_btn = ctk.CTkButton(
            btn_frame, text="📋 PASTE URL", command=self._paste_url,
            width=120, height=36, corner_radius=4,
            fg_color=Flare.FIRE_CRIMSON,
            hover_color=Flare.FIRE,
            text_color=Flare.WHITE,
            font=ctk.CTkFont(size=11, weight="bold")
        )
        paste_btn.pack(side="left", padx=(0, 10))

        # Clear button
        clear_btn = ctk.CTkButton(
            btn_frame, text="✕ CLEAR", command=self._clear_url,
            width=80, height=36, corner_radius=4,
            fg_color="transparent",
            hover_color=Flare.SURFACE_2,
            border_width=1, border_color=Flare.BORDER,
            text_color=Flare.GRAY,
            font=ctk.CTkFont(size=11, weight="bold")
        )
        clear_btn.pack(side="left")

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
        """Footer with branding and update check."""
        footer = ctk.CTkFrame(parent, fg_color="transparent")
        footer.pack(fill="x", pady=(20, 0))

        # Fire accent line
        ctk.CTkFrame(
            footer, fg_color=Flare.FIRE,
            height=2, corner_radius=0
        ).pack(fill="x", pady=(0, 12))

        # Footer row
        footer_row = ctk.CTkFrame(footer, fg_color="transparent")
        footer_row.pack(fill="x")

        # Credits
        ctk.CTkLabel(
            footer_row,
            text="FLARE ECOSYSTEM  •  Powered by yt-dlp  •  Made by Mukund Thiru",
            font=ctk.CTkFont(size=10),
            text_color=Flare.GRAY_DIM
        ).pack(side="left")

        # Update check button
        self.update_label = ctk.CTkLabel(
            footer_row,
            text="",
            font=ctk.CTkFont(size=10),
            text_color=Flare.FIRE
        )
        self.update_label.pack(side="right", padx=(10, 0))

        ctk.CTkButton(
            footer_row,
            text="Check Updates",
            command=self._check_updates,
            width=100, height=24,
            corner_radius=0,
            fg_color="transparent",
            hover_color=Flare.SURFACE_2,
            border_width=1,
            border_color=Flare.BORDER,
            text_color=Flare.GRAY,
            font=ctk.CTkFont(size=9)
        ).pack(side="right")

        # Auto-check for updates on startup (in background)
        self.after(2000, self._check_updates_silent)

    # =========================================================================
    # UPDATE CHECKING
    # =========================================================================
    def _check_updates(self):
        """Check for updates and show result."""
        if not HAS_UPDATER:
            self._log("Updater not available", error=True)
            return

        self._log("Checking for updates...")
        self.update_label.configure(text="Checking...")

        def on_result(has_update, version, notes):
            if has_update:
                self.update_label.configure(text=f"v{version} available!")
                self._log(f"Update available: v{version}")
                if messagebox.askyesno(
                    "Update Available",
                    f"A new version (v{version}) is available!\n\n"
                    f"Current: v{__version__}\n"
                    f"Latest: v{version}\n\n"
                    "Would you like to open the download page?"
                ):
                    import webbrowser
                    webbrowser.open(f"https://github.com/{GITHUB_REPO}/releases/latest")
            else:
                self.update_label.configure(text="Up to date")
                self._log("You have the latest version")

        updater = Updater()
        updater.check_async(on_result)

    def _check_updates_silent(self):
        """Check for updates silently on startup."""
        if not HAS_UPDATER:
            return

        def on_result(has_update, version, notes):
            if has_update:
                self.update_label.configure(text=f"v{version} available!")

        updater = Updater()
        updater.check_async(on_result)

    # =========================================================================
    # ACTIONS
    # =========================================================================
    def _paste_to_entry(self, event=None):
        """Handle Ctrl+V in the URL entry field - let default work or use fallback."""
        try:
            # Try to get clipboard and insert at cursor
            text = self._get_clipboard_text()
            if text:
                # Clear selection if any
                try:
                    self.url_entry.delete("sel.first", "sel.last")
                except:
                    pass
                # Insert at cursor or replace all if empty
                if not self.url_var.get().strip():
                    self.url_var.set(text)
                else:
                    self.url_entry.insert("insert", text)
                return "break"  # Prevent default handling
        except:
            pass
        return None  # Let default handling proceed

    def _get_clipboard_text(self):
        """Get text from clipboard using multiple methods."""
        # Method 1: Windows win32clipboard (most reliable on Windows)
        if sys.platform == 'win32':
            try:
                import ctypes
                from ctypes import wintypes

                CF_UNICODETEXT = 13
                user32 = ctypes.windll.user32
                kernel32 = ctypes.windll.kernel32

                user32.OpenClipboard(0)
                try:
                    if user32.IsClipboardFormatAvailable(CF_UNICODETEXT):
                        data = user32.GetClipboardData(CF_UNICODETEXT)
                        if data:
                            kernel32.GlobalLock.restype = ctypes.c_void_p
                            data_locked = kernel32.GlobalLock(data)
                            if data_locked:
                                text = ctypes.c_wchar_p(data_locked).value
                                kernel32.GlobalUnlock(data)
                                if text:
                                    return text.strip()
                finally:
                    user32.CloseClipboard()
            except:
                pass

        # Method 2: Try tkinter clipboard
        try:
            text = self.clipboard_get()
            if text:
                return text.strip()
        except:
            pass

        # Method 3: PowerShell fallback for Windows
        if sys.platform == 'win32':
            try:
                result = subprocess.run(
                    ['powershell', '-command', 'Get-Clipboard'],
                    capture_output=True, text=True, timeout=3,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                if result.returncode == 0 and result.stdout.strip():
                    return result.stdout.strip()
            except:
                pass

        # Method 4: Linux xclip/xsel
        if sys.platform.startswith('linux'):
            for cmd in [['xclip', '-selection', 'clipboard', '-o'], ['xsel', '--clipboard', '--output']]:
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=2)
                    if result.returncode == 0 and result.stdout.strip():
                        return result.stdout.strip()
                except:
                    pass

        # Method 5: macOS pbpaste
        if sys.platform == 'darwin':
            try:
                result = subprocess.run(['pbpaste'], capture_output=True, text=True, timeout=2)
                if result.returncode == 0 and result.stdout.strip():
                    return result.stdout.strip()
            except:
                pass

        return None

    def _paste_url(self):
        """Paste URL from clipboard."""
        url = self._get_clipboard_text()

        if url:
            self.url_var.set(url)
            self._log("URL pasted")
            # Focus the entry
            self.url_entry.focus_set()
        else:
            self._log("Could not read clipboard", error=True)
            messagebox.showinfo(
                "Paste",
                "Could not access clipboard.\n\n"
                "Try clicking in the URL box and pressing Ctrl+V,\n"
                "or type/paste the URL manually."
            )

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
