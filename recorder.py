import ctypes
import json
import os
import string
import subprocess
import sys
import threading
import time
import wave
import winreg
from ctypes import wintypes
from datetime import datetime

import numpy as np
import soundcard as sc
import sv_ttk
import tkinter as tk
from tkinter import ttk, messagebox

COLOR_READY = "#2fb344"
COLOR_RECORDING = "#e5484d"
COLOR_MUTED = "#888888"

SAMPLE_RATE = 48000
CHANNELS = 2
CHUNK_FRAMES = 1024
DEFAULT_OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Recordings")

APP_DIR = os.path.dirname(os.path.abspath(__file__))
ICONS_DIR = os.path.join(APP_DIR, "icons")
SETTINGS_PATH = os.path.join(APP_DIR, "settings.json")
DEFAULT_ICON = "Wave 5 blocks"
ICON_SECRET_CODE = "1327"
ICON_CODE_TIMEOUT = 2.0  # seconds allowed between keystrokes of the secret code


GA_ROOT = 2


def _get_toplevel_window_rect(widget):
    """Real screen rect of a Tk widget's decorated top-level frame.

    winfo_id() returns Tk's inner client-area HWND, not the OS-decorated
    frame window, so GetWindowRect on it excludes the title bar (same
    offset as winfo_rootx/rooty). GetAncestor(..., GA_ROOT) walks up to
    the actual frame window first.
    """
    child_hwnd = wintypes.HWND(widget.winfo_id())
    frame_hwnd = ctypes.windll.user32.GetAncestor(child_hwnd, GA_ROOT)
    rect = wintypes.RECT()
    ctypes.windll.user32.GetWindowRect(frame_hwnd, ctypes.byref(rect))
    return rect.left, rect.top, rect.right, rect.bottom


DWMWA_USE_IMMERSIVE_DARK_MODE = 20


def _set_titlebar_dark(widget, dark):
    """Match the window's title bar to the ttk theme (Windows 10 1809+/11)."""
    frame_hwnd = ctypes.windll.user32.GetAncestor(wintypes.HWND(widget.winfo_id()), GA_ROOT)
    value = ctypes.c_int(1 if dark else 0)
    ctypes.windll.dwmapi.DwmSetWindowAttribute(
        frame_hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE, ctypes.byref(value), ctypes.sizeof(value)
    )


def _system_uses_light_theme():
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
        )
        value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
        return bool(value)
    except OSError:
        return True


def _load_settings():
    try:
        with open(SETTINGS_PATH, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def _save_settings(settings):
    try:
        with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2)
    except OSError:
        pass


def _available_icons():
    try:
        return sorted(os.path.splitext(n)[0] for n in os.listdir(ICONS_DIR) if n.lower().endswith(".ico"))
    except OSError:
        return []


def apply_icon(root, name):
    """Set the app icon (title bar + taskbar) from icons/<name>.ico; False if it can't be applied."""
    path = os.path.join(ICONS_DIR, name + ".ico")
    if not os.path.isfile(path):
        return False
    try:
        root.iconbitmap(default=path)  # later windows (dialogs) inherit it
        root.iconbitmap(path)          # and the already-open main window switches now
    except tk.TclError:
        return False
    return True


class IconPickerDialog(tk.Toplevel):
    """Hidden icon changer, opened by typing the secret code. Clicking a tile applies that icon at once."""

    COLUMNS = 4

    def __init__(self, parent, current, on_pick):
        super().__init__(parent)
        self.title("Icon")
        self.transient(parent)
        self.resizable(False, False)
        self._on_pick = on_pick
        self._images = []  # Tk drops PhotoImages that nothing references
        self._buttons = {}

        grid = ttk.Frame(self, padding=12)
        grid.pack()
        for index, name in enumerate(_available_icons()):
            try:
                image = tk.PhotoImage(file=os.path.join(ICONS_DIR, name + ".png"))
            except tk.TclError:
                image = None
            self._images.append(image)
            tile = ttk.Frame(grid)
            tile.grid(row=index // self.COLUMNS, column=index % self.COLUMNS, padx=4, pady=6)
            button = ttk.Button(tile, image=image, text=None if image else name, command=lambda n=name: self._pick(n))
            button.pack()
            ttk.Label(tile, text=name, wraplength=100, justify="center", font=("Segoe UI", 8)).pack(pady=(2, 0))
            self._buttons[name] = button
        self._highlight(current)

        parent.update_idletasks()
        _, parent_top, parent_right, _ = _get_toplevel_window_rect(parent)
        self.geometry(f"+{parent_right + 10}+{parent_top}")
        self.update_idletasks()
        _set_titlebar_dark(self, sv_ttk.get_theme() == "dark")
        self.bind("<Escape>", lambda _event: self.destroy())

    def _highlight(self, chosen):
        for name, button in self._buttons.items():
            button.configure(style="Accent.TButton" if name == chosen else "TButton")

    def _pick(self, name):
        self._on_pick(name)
        self._highlight(name)


class FolderBrowserDialog(tk.Toplevel):
    """A pure-Tk folder picker.

    Windows' native folder dialog (SHBrowseForFolder/IFileDialog) can
    deadlock when the calling process never received real OS foreground
    activation (e.g. launched via automation, or in some Windows setups
    even on a normal launch). This dialog avoids the native picker
    entirely by browsing the filesystem with a plain ttk.Treeview.
    """

    def __init__(self, parent, initial_dir):
        super().__init__(parent)
        self.title("Choose Save Folder")
        self.transient(parent)
        self.result = None

        width, height = 420, 420
        parent.update_idletasks()
        _, parent_top, parent_right, _ = _get_toplevel_window_rect(parent)
        x = parent_right + 10
        y = parent_top
        self.geometry(f"{width}x{height}+{x}+{y}")
        self.update_idletasks()
        _set_titlebar_dark(self, sv_ttk.get_theme() == "dark")

        self.tree = ttk.Treeview(self, show="tree")
        self.tree.pack(fill="both", expand=True, padx=8, pady=(8, 4))
        self.tree.bind("<<TreeviewOpen>>", self._on_open)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        self.path_var = tk.StringVar(value=initial_dir)
        ttk.Entry(self, textvariable=self.path_var).pack(fill="x", padx=8, pady=(0, 8))

        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", padx=8, pady=(0, 8))
        ttk.Button(btn_frame, text="Select Folder", command=self._on_ok).pack(side="right")
        ttk.Button(btn_frame, text="Cancel", command=self._on_cancel).pack(side="right", padx=(0, 6))

        self._populate_roots()
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)

        self.grab_set()
        self.wait_window(self)

    def _list_subdirs(self, path):
        try:
            return sorted(
                e for e in os.listdir(path) if os.path.isdir(os.path.join(path, e))
            )
        except OSError:
            return []

    def _add_node(self, parent, text, path):
        node = self.tree.insert(parent, "end", text=text, values=[path])
        self.tree.insert(node, "end", text="")  # placeholder so the expand arrow shows
        return node

    def _populate_roots(self):
        for letter in string.ascii_uppercase:
            drive = f"{letter}:\\"
            if os.path.exists(drive):
                self._add_node("", drive, drive)

    def _node_path(self, node):
        values = self.tree.item(node, "values")
        return values[0] if values else ""

    def _on_open(self, _event):
        node = self.tree.focus()
        children = self.tree.get_children(node)
        if len(children) == 1 and self.tree.item(children[0], "text") == "":
            self.tree.delete(children[0])
            path = self._node_path(node)
            for name in self._list_subdirs(path):
                self._add_node(node, name, os.path.join(path, name))

    def _on_select(self, _event):
        node = self.tree.focus()
        path = self._node_path(node)
        if path:
            self.path_var.set(path)

    def _on_ok(self):
        self.result = self.path_var.get().strip()
        self.destroy()

    def _on_cancel(self):
        self.result = None
        self.destroy()


class RecorderApp:
    def __init__(self, root, icon_name=DEFAULT_ICON):
        self.root = root
        self.root.title("System Audio Recorder")
        self.root.resizable(False, False)

        self.icon_name = icon_name
        self._icon_picker = None
        self._code_buffer = ""
        self._code_last = 0.0
        self.root.bind_all("<Key>", self._on_key, add="+")

        self.is_recording = False
        self.record_thread = None
        self.stop_event = threading.Event()
        self.start_time = None
        self.current_path = None

        self.speakers = sc.all_speakers()
        self.speaker_names = [s.name for s in self.speakers]
        default_speaker = sc.default_speaker()

        outer = ttk.Frame(root, padding=16)
        outer.grid()

        toolbar = ttk.Frame(outer)
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        ttk.Button(
            toolbar, text="\U0001F504  Refresh", command=self.refresh_app
        ).pack(side="right")

        source_frame = ttk.LabelFrame(outer, text="Audio Source", padding=12)
        source_frame.grid(row=1, column=0, sticky="ew")
        self.device_var = tk.StringVar(value=default_speaker.name if default_speaker else self.speaker_names[0])
        self.device_combo = ttk.Combobox(
            source_frame, textvariable=self.device_var, values=self.speaker_names, state="readonly"
        )
        self.device_combo.pack(fill="x")

        save_frame = ttk.LabelFrame(outer, text="Save Location", padding=12)
        save_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        self.output_dir_var = tk.StringVar(value=DEFAULT_OUTPUT_DIR)
        self.output_dir_entry = ttk.Entry(save_frame, textvariable=self.output_dir_var, width=42)
        self.output_dir_entry.pack(fill="x")
        self.browse_button = ttk.Button(
            save_frame, text="\U0001F4C1  Browse...", command=self.browse_folder
        )
        self.browse_button.pack(fill="x", pady=(6, 0))

        status_row = ttk.Frame(outer)
        status_row.grid(row=3, column=0, sticky="ew", pady=(14, 10))
        self.status_var = tk.StringVar(value="●  Ready")
        self.status_label = ttk.Label(
            status_row, textvariable=self.status_var, font=("Segoe UI", 11, "bold"), foreground=COLOR_READY
        )
        self.status_label.pack(side="left")

        self.toggle_button = ttk.Button(
            outer, text="Start Recording", style="Accent.TButton", command=self.toggle_recording
        )
        self.toggle_button.grid(row=4, column=0, sticky="ew", ipady=4)

        # Fixed height reserves room for up to 3 lines of path text up front
        # (label line + folder, which can itself wrap, + filename), so it
        # can never grow the row once a path is shown (window isn't
        # resizable). Open Folder docks to the right, square-ish,
        # height-matched to the row via fill="y".
        file_row = ttk.Frame(outer, height=62)
        file_row.grid(row=5, column=0, sticky="ew", pady=(12, 0))
        file_row.grid_propagate(False)

        self.open_folder_button = ttk.Button(
            file_row, text="\U0001F4C2", width=3, command=self.open_containing_folder, state="disabled"
        )
        self.open_folder_button.pack(side="right", fill="y")

        self.file_var = tk.StringVar(value="")
        self.file_label = ttk.Label(
            file_row, textvariable=self.file_var, foreground=COLOR_MUTED, justify="left", wraplength=320
        )
        self.file_label.pack(side="left", fill="both", expand=True, padx=(0, 8))

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self._center_window()
        self.root.update_idletasks()
        _set_titlebar_dark(self.root, sv_ttk.get_theme() == "dark")
        self._tick()

    def _center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() - width) // 2
        y = (self.root.winfo_screenheight() - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def _on_key(self, event):
        if event.widget.winfo_toplevel() is not self.root:
            return
        now = time.monotonic()
        if now - self._code_last > ICON_CODE_TIMEOUT:
            self._code_buffer = ""
        self._code_last = now
        if not (event.char and event.char.isprintable()):
            return
        self._code_buffer = (self._code_buffer + event.char)[-len(ICON_SECRET_CODE):]
        if self._code_buffer != ICON_SECRET_CODE:
            return
        self._code_buffer = ""
        widget = event.widget
        if isinstance(widget, ttk.Entry) and str(widget.cget("state")) == "normal":
            text = widget.get()
            if text.endswith(ICON_SECRET_CODE):  # the digits were typed into the folder field: take them back out
                widget.delete(len(text) - len(ICON_SECRET_CODE), "end")
        self.open_icon_picker()

    def open_icon_picker(self):
        if self._icon_picker is not None and self._icon_picker.winfo_exists():
            self._icon_picker.lift()
            return
        self._icon_picker = IconPickerDialog(self.root, self.icon_name, self._set_icon)

    def _set_icon(self, name):
        if apply_icon(self.root, name):
            self.icon_name = name
            settings = _load_settings()
            settings["icon"] = name
            _save_settings(settings)

    def toggle_recording(self):
        if self.is_recording:
            self.stop_recording()
        else:
            self.start_recording()

    def start_recording(self):
        output_dir = self.output_dir_var.get().strip()
        if not output_dir:
            messagebox.showerror("Error", "Please choose a save folder.")
            return
        try:
            os.makedirs(output_dir, exist_ok=True)
        except OSError as exc:
            messagebox.showerror("Error", f"Could not create save folder:\n{exc}")
            return

        device_name = self.device_var.get()
        speaker = next((s for s in self.speakers if s.name == device_name), None)
        if speaker is None:
            messagebox.showerror("Error", "Selected device not found.")
            return

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.current_path = os.path.join(output_dir, f"recording_{timestamp}.wav")

        self.stop_event.clear()
        self.is_recording = True
        self.start_time = time.time()
        self.toggle_button.config(text="Stop Recording")
        self.device_combo.config(state="disabled")
        self.output_dir_entry.config(state="disabled")
        self.browse_button.config(state="disabled")
        self.file_var.set(f"Saving to: {output_dir}\\\n{os.path.basename(self.current_path)}")
        self.open_folder_button.config(state="normal")
        self.status_label.config(foreground=COLOR_RECORDING)
        self.status_var.set("●  Recording  00:00")

        self.record_thread = threading.Thread(
            target=self._record_loop, args=(speaker, self.current_path), daemon=True
        )
        self.record_thread.start()

    def stop_recording(self):
        self.stop_event.set()
        self.is_recording = False
        self.toggle_button.config(text="Start Recording")
        self.device_combo.config(state="readonly")
        self.output_dir_entry.config(state="normal")
        self.browse_button.config(state="normal")
        self.status_label.config(foreground=COLOR_READY)
        self.status_var.set("●  Ready")

    def browse_folder(self):
        dialog = FolderBrowserDialog(self.root, self.output_dir_var.get() or DEFAULT_OUTPUT_DIR)
        if dialog.result:
            self.output_dir_var.set(dialog.result)

    def open_containing_folder(self):
        if self.current_path:
            target = os.path.dirname(self.current_path)
        else:
            target = self.output_dir_var.get().strip() or DEFAULT_OUTPUT_DIR
        if not os.path.isdir(target):
            messagebox.showerror("Error", f"Folder does not exist:\n{target}")
            return
        os.startfile(target)

    def _record_loop(self, speaker, path):
        wav_file = wave.open(path, "wb")
        wav_file.setnchannels(CHANNELS)
        wav_file.setsampwidth(2)  # 16-bit PCM
        wav_file.setframerate(SAMPLE_RATE)

        try:
            loopback_mic = sc.get_microphone(id=speaker.id, include_loopback=True)
            with loopback_mic.recorder(samplerate=SAMPLE_RATE, channels=CHANNELS) as mic:
                while not self.stop_event.is_set():
                    data = mic.record(numframes=CHUNK_FRAMES)
                    clipped = np.clip(data, -1.0, 1.0)
                    pcm16 = (clipped * 32767).astype(np.int16)
                    wav_file.writeframes(pcm16.tobytes())
        except Exception as exc:
            self.root.after(0, lambda: messagebox.showerror("Recording error", str(exc)))
        finally:
            wav_file.close()

    def _tick(self):
        if self.is_recording and self.start_time:
            elapsed = int(time.time() - self.start_time)
            mins, secs = divmod(elapsed, 60)
            self.status_var.set(f"●  Recording  {mins:02d}:{secs:02d}")
        self.root.after(500, self._tick)

    def on_close(self):
        if self.is_recording:
            self.stop_recording()
            time.sleep(0.2)
        self.root.destroy()

    def refresh_app(self):
        """Relaunch the app from scratch, like closing and reopening it.

        os.execv's Windows emulation (spawn-wait-exit via MSVCRT) is
        unreliable for a windowless pythonw GUI process, so spawn a fresh
        independent process directly and exit this one instead.
        """
        if self.is_recording:
            self.stop_recording()
            time.sleep(0.2)
        subprocess.Popen([sys.executable] + sys.argv, close_fds=True)
        self.root.destroy()
        os._exit(0)


def main():
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("AudioRecorder.WavRecorder")
    root = tk.Tk()
    saved_icon = _load_settings().get("icon")
    icon_name = saved_icon if saved_icon in _available_icons() else DEFAULT_ICON
    apply_icon(root, icon_name)
    sv_ttk.set_theme("light" if _system_uses_light_theme() else "dark")
    RecorderApp(root, icon_name)
    root.mainloop()


if __name__ == "__main__":
    main()
