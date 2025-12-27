#!/usr/bin/env python3
"""
NeonTube Installer - Cross-platform GUI Installer
Provides a user-friendly installation experience
"""

import os
import sys
import platform
import subprocess
import threading
import shutil
from pathlib import Path

# Check for tkinter availability
try:
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog
    HAS_TK = True
except ImportError:
    HAS_TK = False


class InstallerGUI:
    """Cross-platform GUI installer for NeonTube"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("NeonTube Installer")
        self.root.geometry("600x500")
        self.root.resizable(False, False)

        # Colors
        self.bg_dark = "#0a0a0f"
        self.bg_medium = "#12121a"
        self.accent = "#00d4ff"
        self.text = "#ffffff"
        self.text_dim = "#8888aa"

        self.root.configure(bg=self.bg_dark)

        # Installation path
        self.system = platform.system()
        if self.system == "Windows":
            default_path = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'NeonTube')
        elif self.system == "Darwin":  # macOS
            default_path = os.path.expanduser("~/Applications/NeonTube")
        else:  # Linux
            default_path = os.path.expanduser("~/.local/share/neontube")

        self.install_path = tk.StringVar(value=default_path)
        self.create_shortcut = tk.BooleanVar(value=True)
        self.install_ffmpeg = tk.BooleanVar(value=True)

        self.create_ui()

    def create_ui(self):
        """Create the installer UI"""
        # Header
        header = tk.Frame(self.root, bg=self.bg_medium, height=100)
        header.pack(fill="x")
        header.pack_propagate(False)

        title = tk.Label(
            header,
            text="NEONTUBE",
            font=("Segoe UI", 32, "bold"),
            fg=self.accent,
            bg=self.bg_medium
        )
        title.pack(pady=(20, 5))

        subtitle = tk.Label(
            header,
            text="Video Downloader Installation",
            font=("Segoe UI", 12),
            fg=self.text_dim,
            bg=self.bg_medium
        )
        subtitle.pack()

        # Main content
        content = tk.Frame(self.root, bg=self.bg_dark, padx=40, pady=20)
        content.pack(fill="both", expand=True)

        # Installation path
        path_label = tk.Label(
            content,
            text="Installation Directory:",
            font=("Segoe UI", 11),
            fg=self.text,
            bg=self.bg_dark,
            anchor="w"
        )
        path_label.pack(fill="x", pady=(0, 5))

        path_frame = tk.Frame(content, bg=self.bg_dark)
        path_frame.pack(fill="x", pady=(0, 20))

        path_entry = tk.Entry(
            path_frame,
            textvariable=self.install_path,
            font=("Segoe UI", 10),
            bg=self.bg_medium,
            fg=self.text,
            insertbackground=self.text,
            relief="flat",
            highlightthickness=1,
            highlightcolor=self.accent,
            highlightbackground=self.bg_medium
        )
        path_entry.pack(side="left", fill="x", expand=True, ipady=8)

        browse_btn = tk.Button(
            path_frame,
            text="Browse",
            font=("Segoe UI", 10),
            bg=self.bg_medium,
            fg=self.text,
            relief="flat",
            cursor="hand2",
            command=self.browse_path
        )
        browse_btn.pack(side="right", padx=(10, 0), ipady=5, ipadx=15)

        # Options
        options_label = tk.Label(
            content,
            text="Installation Options:",
            font=("Segoe UI", 11),
            fg=self.text,
            bg=self.bg_dark,
            anchor="w"
        )
        options_label.pack(fill="x", pady=(0, 10))

        # Shortcut checkbox
        shortcut_check = tk.Checkbutton(
            content,
            text="Create desktop shortcut",
            variable=self.create_shortcut,
            font=("Segoe UI", 10),
            fg=self.text,
            bg=self.bg_dark,
            selectcolor=self.bg_medium,
            activebackground=self.bg_dark,
            activeforeground=self.text,
            cursor="hand2"
        )
        shortcut_check.pack(anchor="w", pady=2)

        # FFmpeg checkbox
        ffmpeg_check = tk.Checkbutton(
            content,
            text="Download FFmpeg (required for video merging)",
            variable=self.install_ffmpeg,
            font=("Segoe UI", 10),
            fg=self.text,
            bg=self.bg_dark,
            selectcolor=self.bg_medium,
            activebackground=self.bg_dark,
            activeforeground=self.text,
            cursor="hand2"
        )
        ffmpeg_check.pack(anchor="w", pady=2)

        # Progress section
        self.progress_frame = tk.Frame(content, bg=self.bg_dark)
        self.progress_frame.pack(fill="x", pady=(20, 0))

        self.status_label = tk.Label(
            self.progress_frame,
            text="Ready to install",
            font=("Segoe UI", 10),
            fg=self.text_dim,
            bg=self.bg_dark
        )
        self.status_label.pack(anchor="w")

        self.progress_bar = ttk.Progressbar(
            self.progress_frame,
            mode='determinate',
            length=520
        )
        self.progress_bar.pack(fill="x", pady=(5, 0))

        # Log area
        self.log_text = tk.Text(
            content,
            height=6,
            font=("Consolas", 9),
            bg=self.bg_medium,
            fg=self.text_dim,
            relief="flat",
            wrap="word"
        )
        self.log_text.pack(fill="x", pady=(15, 0))

        # Buttons
        button_frame = tk.Frame(self.root, bg=self.bg_dark, pady=20)
        button_frame.pack(fill="x")

        self.install_btn = tk.Button(
            button_frame,
            text="INSTALL",
            font=("Segoe UI", 14, "bold"),
            bg=self.accent,
            fg=self.bg_dark,
            relief="flat",
            cursor="hand2",
            command=self.start_installation,
            width=20
        )
        self.install_btn.pack(pady=10, ipady=10)

    def browse_path(self):
        """Open folder browser"""
        path = filedialog.askdirectory(initialdir=self.install_path.get())
        if path:
            self.install_path.set(path)

    def log(self, message):
        """Add message to log"""
        self.log_text.insert("end", f"{message}\n")
        self.log_text.see("end")
        self.root.update()

    def update_status(self, message, progress=None):
        """Update status and progress"""
        self.status_label.config(text=message)
        if progress is not None:
            self.progress_bar['value'] = progress
        self.root.update()

    def start_installation(self):
        """Start the installation process"""
        self.install_btn.config(state="disabled", text="INSTALLING...")
        thread = threading.Thread(target=self.install, daemon=True)
        thread.start()

    def install(self):
        """Perform the installation"""
        try:
            install_dir = self.install_path.get()
            source_dir = os.path.dirname(os.path.abspath(__file__))

            # Step 1: Create installation directory
            self.update_status("Creating installation directory...", 10)
            self.log(f"[*] Creating directory: {install_dir}")
            os.makedirs(install_dir, exist_ok=True)

            # Step 2: Copy application files
            self.update_status("Copying application files...", 20)
            files_to_copy = [
                'youtube_downloader.py',
                'updater.py',
                'version.py',
                'requirements.txt',
                'README.md'
            ]

            for filename in files_to_copy:
                src = os.path.join(source_dir, filename)
                if os.path.exists(src):
                    shutil.copy2(src, install_dir)
                    self.log(f"[+] Copied: {filename}")

            # Step 3: Create virtual environment
            self.update_status("Creating virtual environment...", 35)
            self.log("[*] Creating Python virtual environment...")
            venv_path = os.path.join(install_dir, 'venv')

            subprocess.run(
                [sys.executable, '-m', 'venv', venv_path],
                check=True,
                capture_output=True
            )
            self.log("[+] Virtual environment created")

            # Step 4: Install dependencies
            self.update_status("Installing dependencies...", 50)
            self.log("[*] Installing Python packages...")

            if self.system == "Windows":
                pip_path = os.path.join(venv_path, 'Scripts', 'pip.exe')
                python_path = os.path.join(venv_path, 'Scripts', 'python.exe')
            else:
                pip_path = os.path.join(venv_path, 'bin', 'pip')
                python_path = os.path.join(venv_path, 'bin', 'python')

            requirements_path = os.path.join(install_dir, 'requirements.txt')

            subprocess.run(
                [pip_path, 'install', '--upgrade', 'pip'],
                check=True,
                capture_output=True
            )

            subprocess.run(
                [pip_path, 'install', '-r', requirements_path],
                check=True,
                capture_output=True
            )
            self.log("[+] Dependencies installed")

            # Step 5: Install yt-dlp
            self.update_status("Installing yt-dlp...", 65)
            self.log("[*] Installing yt-dlp...")
            subprocess.run(
                [pip_path, 'install', 'yt-dlp'],
                check=True,
                capture_output=True
            )
            self.log("[+] yt-dlp installed")

            # Step 6: Create launcher scripts
            self.update_status("Creating launcher...", 75)
            self.create_launcher(install_dir, python_path)
            self.log("[+] Launcher created")

            # Step 7: Create desktop shortcut
            if self.create_shortcut.get():
                self.update_status("Creating desktop shortcut...", 85)
                self.create_desktop_shortcut(install_dir)
                self.log("[+] Desktop shortcut created")

            # Step 8: Install FFmpeg (optional)
            if self.install_ffmpeg.get():
                self.update_status("Setting up FFmpeg...", 90)
                self.setup_ffmpeg(install_dir)

            # Complete
            self.update_status("Installation complete!", 100)
            self.log("\n[+] NeonTube installed successfully!")
            self.log(f"[+] Location: {install_dir}")

            self.root.after(0, lambda: self.install_btn.config(
                state="normal",
                text="LAUNCH APP",
                command=lambda: self.launch_app(install_dir)
            ))

            self.root.after(0, lambda: messagebox.showinfo(
                "Installation Complete",
                f"NeonTube has been installed successfully!\n\nLocation: {install_dir}"
            ))

        except Exception as e:
            self.log(f"\n[!] Error: {str(e)}")
            self.update_status("Installation failed!", 0)
            self.root.after(0, lambda: self.install_btn.config(
                state="normal",
                text="RETRY"
            ))
            self.root.after(0, lambda: messagebox.showerror(
                "Installation Failed",
                f"An error occurred:\n{str(e)}"
            ))

    def create_launcher(self, install_dir, python_path):
        """Create platform-specific launcher"""
        if self.system == "Windows":
            launcher_path = os.path.join(install_dir, 'NeonTube.bat')
            with open(launcher_path, 'w') as f:
                f.write(f'@echo off\n')
                f.write(f'cd /d "{install_dir}"\n')
                f.write(f'call venv\\Scripts\\activate.bat\n')
                f.write(f'pythonw youtube_downloader.py\n')

            # Create VBS to hide console window
            vbs_path = os.path.join(install_dir, 'NeonTube.vbs')
            with open(vbs_path, 'w') as f:
                f.write(f'Set WshShell = CreateObject("WScript.Shell")\n')
                f.write(f'WshShell.Run chr(34) & "{launcher_path}" & chr(34), 0\n')
                f.write(f'Set WshShell = Nothing\n')

        else:  # Linux/macOS
            launcher_path = os.path.join(install_dir, 'neontube')
            with open(launcher_path, 'w') as f:
                f.write('#!/bin/bash\n')
                f.write(f'cd "{install_dir}"\n')
                f.write('source venv/bin/activate\n')
                f.write('python3 youtube_downloader.py\n')
            os.chmod(launcher_path, 0o755)

    def create_desktop_shortcut(self, install_dir):
        """Create desktop shortcut"""
        if self.system == "Windows":
            desktop = os.path.join(os.environ['USERPROFILE'], 'Desktop')
            shortcut_path = os.path.join(desktop, 'NeonTube.lnk')
            vbs_path = os.path.join(install_dir, 'NeonTube.vbs')

            # Use PowerShell to create shortcut
            ps_command = f'''
            $WshShell = New-Object -comObject WScript.Shell
            $Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
            $Shortcut.TargetPath = "wscript.exe"
            $Shortcut.Arguments = '"{vbs_path}"'
            $Shortcut.WorkingDirectory = "{install_dir}"
            $Shortcut.Description = "NeonTube Video Downloader"
            $Shortcut.Save()
            '''
            subprocess.run(['powershell', '-Command', ps_command], capture_output=True)

        elif self.system == "Darwin":  # macOS
            # Create .app bundle structure
            app_path = os.path.expanduser("~/Desktop/NeonTube.app")
            contents_path = os.path.join(app_path, "Contents")
            macos_path = os.path.join(contents_path, "MacOS")
            os.makedirs(macos_path, exist_ok=True)

            # Create launcher script
            launcher = os.path.join(macos_path, "NeonTube")
            with open(launcher, 'w') as f:
                f.write('#!/bin/bash\n')
                f.write(f'cd "{install_dir}"\n')
                f.write('source venv/bin/activate\n')
                f.write('python3 youtube_downloader.py\n')
            os.chmod(launcher, 0o755)

            # Create Info.plist
            plist_path = os.path.join(contents_path, "Info.plist")
            with open(plist_path, 'w') as f:
                f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                f.write('<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">\n')
                f.write('<plist version="1.0">\n')
                f.write('<dict>\n')
                f.write('    <key>CFBundleExecutable</key>\n')
                f.write('    <string>NeonTube</string>\n')
                f.write('    <key>CFBundleName</key>\n')
                f.write('    <string>NeonTube</string>\n')
                f.write('</dict>\n')
                f.write('</plist>\n')

        else:  # Linux
            desktop_file = os.path.expanduser("~/.local/share/applications/neontube.desktop")
            os.makedirs(os.path.dirname(desktop_file), exist_ok=True)

            launcher_path = os.path.join(install_dir, 'neontube')
            with open(desktop_file, 'w') as f:
                f.write('[Desktop Entry]\n')
                f.write('Name=NeonTube\n')
                f.write('Comment=Video Downloader\n')
                f.write(f'Exec={launcher_path}\n')
                f.write('Icon=video-x-generic\n')
                f.write('Terminal=false\n')
                f.write('Type=Application\n')
                f.write('Categories=Network;AudioVideo;\n')

            # Also create on desktop
            desktop_link = os.path.expanduser("~/Desktop/NeonTube.desktop")
            shutil.copy(desktop_file, desktop_link)
            os.chmod(desktop_link, 0o755)

    def setup_ffmpeg(self, install_dir):
        """Setup FFmpeg"""
        self.log("[*] Checking FFmpeg...")

        # Check if FFmpeg is already installed
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
            self.log("[+] FFmpeg already installed")
            return
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

        self.log("[~] FFmpeg not found - please install manually:")
        if self.system == "Windows":
            self.log("    Download from: https://ffmpeg.org/download.html")
        elif self.system == "Darwin":
            self.log("    Run: brew install ffmpeg")
        else:
            self.log("    Run: sudo apt install ffmpeg")

    def launch_app(self, install_dir):
        """Launch the installed application"""
        if self.system == "Windows":
            vbs_path = os.path.join(install_dir, 'NeonTube.vbs')
            os.startfile(vbs_path)
        else:
            launcher_path = os.path.join(install_dir, 'neontube')
            subprocess.Popen([launcher_path])

        self.root.destroy()

    def run(self):
        """Start the installer"""
        self.root.mainloop()


def run_cli_installer():
    """Command-line installer for systems without GUI"""
    print("\n" + "=" * 50)
    print("       NEONTUBE INSTALLER (CLI Mode)")
    print("=" * 50 + "\n")

    system = platform.system()

    # Determine install path
    if system == "Windows":
        default_path = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'NeonTube')
    elif system == "Darwin":
        default_path = os.path.expanduser("~/Applications/NeonTube")
    else:
        default_path = os.path.expanduser("~/.local/share/neontube")

    print(f"Default installation path: {default_path}")
    custom_path = input("Press Enter to accept or enter custom path: ").strip()
    install_dir = custom_path if custom_path else default_path

    print(f"\nInstalling to: {install_dir}\n")

    # Create directory
    os.makedirs(install_dir, exist_ok=True)
    print("[+] Created installation directory")

    # Copy files
    source_dir = os.path.dirname(os.path.abspath(__file__))
    for f in ['youtube_downloader.py', 'updater.py', 'version.py', 'requirements.txt']:
        src = os.path.join(source_dir, f)
        if os.path.exists(src):
            shutil.copy2(src, install_dir)
            print(f"[+] Copied: {f}")

    # Create venv
    print("[*] Creating virtual environment...")
    venv_path = os.path.join(install_dir, 'venv')
    subprocess.run([sys.executable, '-m', 'venv', venv_path], check=True)

    # Install dependencies
    print("[*] Installing dependencies...")
    if system == "Windows":
        pip_path = os.path.join(venv_path, 'Scripts', 'pip')
    else:
        pip_path = os.path.join(venv_path, 'bin', 'pip')

    subprocess.run([pip_path, 'install', '-r', os.path.join(install_dir, 'requirements.txt')], check=True)
    subprocess.run([pip_path, 'install', 'yt-dlp'], check=True)

    print("\n" + "=" * 50)
    print("       INSTALLATION COMPLETE!")
    print("=" * 50)
    print(f"\nInstalled to: {install_dir}")
    print("\nTo run NeonTube:")
    if system == "Windows":
        print(f"  cd {install_dir}")
        print("  venv\\Scripts\\activate")
        print("  python youtube_downloader.py")
    else:
        print(f"  cd {install_dir}")
        print("  source venv/bin/activate")
        print("  python3 youtube_downloader.py")


def main():
    """Main entry point"""
    if HAS_TK:
        try:
            app = InstallerGUI()
            app.run()
        except Exception:
            run_cli_installer()
    else:
        run_cli_installer()


if __name__ == "__main__":
    main()
