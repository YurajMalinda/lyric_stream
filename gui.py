#!/usr/bin/env python3
"""
LyricStream - GUI.

Song info, Play/Pause/Stop, volume, theme, font. Typing speed from songs.json.
Requires: pygame, tkinter (python3-tk on Linux). Optional: ttkbootstrap for dark theme.
"""

import os
import sys
import time
import threading

try:
    import pygame
except ImportError:
    print("Error: pygame is not installed.")
    print("Run: source .venv/bin/activate && pip install pygame")
    sys.exit(1)

import tkinter as tk
from tkinter import messagebox, ttk, scrolledtext

USE_TTKBOOTSTRAP = False
try:
    import ttkbootstrap as ttk_bs
    from ttkbootstrap.widgets.scrolled import ScrolledText
    ttk = ttk_bs
    USE_TTKBOOTSTRAP = True
except ImportError:
    ScrolledText = scrolledtext.ScrolledText

from typewriter.songs_loader import load_songs, get_song, list_songs
from typewriter.display import THEMES, get_theme_list
from typewriter.player import iter_lyrics, get_audio_path, get_line_delay, get_char_delay

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))


# Theme colors for lyric display
THEME_COLORS_HEX = {
    "red": "#ff6b6b",
    "green": "#51cf66",
    "yellow": "#fcc419",
    "blue": "#339af0",
    "magenta": "#cc5de8",
    "cyan": "#22b8cf",
    "white": "#f8f9fa",
}
DEFAULT_TEXT_COLOR = "#dee2e6"


class LyricStreamGUI:
    """LyricStream GUI with dark theme and playback controls."""

    def __init__(self):
        if USE_TTKBOOTSTRAP:
            self.root = ttk.Window(
                title="LyricStream",
                themename="cyborg",
                size=(700, 580),
                minsize=(500, 400),
                resizable=(True, True),
            )
            self.root.place_window_center()
        else:
            self.root = tk.Tk()
            self.root.title("LyricStream")
            self.root.geometry("700x580")
            self.root.minsize(500, 400)

        self.songs = load_songs()
        self.current_song = None
        self.playing = False
        self.paused = False
        self.stop_requested = False
        self.playback_thread = None

        self._build_ui()
        self._bind_shortcuts()

    def _build_ui(self):
        # Header: Song info
        header = ttk.Frame(self.root, padding=15)
        header.pack(fill=tk.X)
        self.song_title_var = tk.StringVar(value="Select a song")
        self.song_artist_var = tk.StringVar(value="")
        title_lbl = ttk.Label(header, textvariable=self.song_title_var, font=("Segoe UI", 16, "bold"))
        if USE_TTKBOOTSTRAP:
            title_lbl.configure(bootstyle="primary")
        title_lbl.pack(anchor=tk.W)
        artist_lbl = ttk.Label(header, textvariable=self.song_artist_var, font=("Segoe UI", 10))
        if USE_TTKBOOTSTRAP:
            artist_lbl.configure(bootstyle="secondary")
        artist_lbl.pack(anchor=tk.W)

        # Controls
        ctrl = ttk.Labelframe(self.root, text="Controls", padding=15)
        ctrl.pack(fill=tk.X, padx=15, pady=(0, 10))

        # Row 1: Song, Theme
        row1 = ttk.Frame(ctrl)
        row1.pack(fill=tk.X, pady=(0, 8))
        ttk.Label(row1, text="Song", width=8).pack(side=tk.LEFT, padx=(0, 8))
        self.song_var = tk.StringVar()
        ids = [s["id"] for s in self.songs]
        self.song_combo = ttk.Combobox(
            row1, textvariable=self.song_var, values=ids, state="readonly", width=28
        )
        if ids:
            self.song_combo.set(ids[0])
            self._on_song_select()
        self.song_combo.pack(side=tk.LEFT, padx=(0, 20))
        self.song_combo.bind("<<ComboboxSelected>>", lambda e: self._on_song_select())

        ttk.Label(row1, text="Theme", width=6).pack(side=tk.LEFT, padx=(20, 8))
        self.theme_var = tk.StringVar(value="plain")
        ttk.Combobox(
            row1,
            textvariable=self.theme_var,
            values=get_theme_list(),
            state="readonly",
            width=10,
        ).pack(side=tk.LEFT)

        # Row 2: Start, Volume
        row2 = ttk.Frame(ctrl)
        row2.pack(fill=tk.X, pady=(0, 8))
        ttk.Label(row2, text="Start (s)").pack(side=tk.LEFT, padx=(0, 5))
        self.start_var = tk.StringVar(value="0")
        ttk.Entry(row2, textvariable=self.start_var, width=6).pack(side=tk.LEFT, padx=(0, 20))

        ttk.Label(row2, text="Volume").pack(side=tk.LEFT, padx=(20, 5))
        self.volume_var = tk.DoubleVar(value=1.0)
        vol_scale = ttk.Scale(row2, from_=0, to=1, variable=self.volume_var, length=80)
        if USE_TTKBOOTSTRAP:
            vol_scale.configure(bootstyle="primary")
        vol_scale.pack(side=tk.LEFT, padx=(0, 5))
        self.volume_var.trace_add("write", lambda *a: self._update_volume())

        # Row 3: Font, Size
        row3 = ttk.Frame(ctrl)
        row3.pack(fill=tk.X, pady=(0, 8))
        ttk.Label(row3, text="Font", width=8).pack(side=tk.LEFT, padx=(0, 8))
        self.font_var = tk.StringVar(value="Consolas")
        font_opts = ["Consolas", "Monaco", "Courier New", "Georgia", "Times New Roman", "Arial", "Segoe UI"]
        ttk.Combobox(row3, textvariable=self.font_var, values=font_opts, state="readonly", width=14).pack(side=tk.LEFT, padx=(0, 20))
        self.font_var.trace_add("write", lambda *a: self._apply_display_style())

        ttk.Label(row3, text="Size", width=4).pack(side=tk.LEFT, padx=(20, 5))
        self.font_size_var = tk.IntVar(value=14)
        ttk.Spinbox(row3, from_=10, to=28, textvariable=self.font_size_var, width=4).pack(side=tk.LEFT, padx=(0, 20))
        self.font_size_var.trace_add("write", lambda *a: self._apply_display_style())

        # Row 4: Buttons
        btn_frame = ttk.Frame(ctrl)
        btn_frame.pack(fill=tk.X, pady=(8, 0))
        self.play_btn = ttk.Button(btn_frame, text="▶ Play", command=self._on_play, width=10)
        if USE_TTKBOOTSTRAP:
            self.play_btn.configure(bootstyle="success")
        self.play_btn.pack(side=tk.LEFT, padx=(0, 8))
        self.pause_btn = ttk.Button(btn_frame, text="⏸ Pause", command=self._on_pause, width=10, state=tk.DISABLED)
        if USE_TTKBOOTSTRAP:
            self.pause_btn.configure(bootstyle="warning")
        self.pause_btn.pack(side=tk.LEFT, padx=(0, 8))
        self.stop_btn = ttk.Button(btn_frame, text="⏹ Stop", command=self._on_stop, width=10, state=tk.DISABLED)
        if USE_TTKBOOTSTRAP:
            self.stop_btn.configure(bootstyle="danger")
        self.stop_btn.pack(side=tk.LEFT)

        # Lyric display
        lyric_frame = ttk.Labelframe(self.root, text="Lyrics", padding=15)
        lyric_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        self._font_family = "Consolas"
        self._font_size = 14
        st_kw = {"font": (self._font_family, self._font_size), "height": 12, "wrap": tk.WORD, "bg": "#1a1a2e", "fg": DEFAULT_TEXT_COLOR, "insertbackground": DEFAULT_TEXT_COLOR}
        if USE_TTKBOOTSTRAP:
            st_kw.update(autohide=True, bootstyle="dark")
        self.text = ScrolledText(lyric_frame, **st_kw)
        self.text.pack(fill=tk.BOTH, expand=True)
        self._text_widget = getattr(self.text, "text", self.text)

        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, font=("Segoe UI", 9))
        if USE_TTKBOOTSTRAP:
            status_bar.configure(bootstyle="secondary")
        status_bar.pack(fill=tk.X, padx=15, pady=(0, 10))

        self._apply_display_style()

    def _bind_shortcuts(self):
        self.root.bind("<space>", lambda e: self._toggle_play_pause())
        self.root.bind("<Escape>", lambda e: self._on_stop())
        self.root.bind("<Return>", lambda e: self._on_play())

    def _on_song_select(self):
        sid = self.song_var.get()
        if not sid:
            return
        song = get_song(sid)
        if song:
            self.song_title_var.set(song.get("title", sid))
            self.song_artist_var.set(song.get("artist", "") or "—")

    def _apply_display_style(self):
        try:
            fam = self.font_var.get() or "Consolas"
            sz = self.font_size_var.get()
            if isinstance(sz, str):
                sz = int(sz) if sz.isdigit() else 14
            self._font_family = fam
            self._font_size = max(10, min(28, sz))
            self._text_widget.configure(font=(self._font_family, self._font_size))
        except Exception:
            pass

    def _update_volume(self):
        try:
            vol = self.volume_var.get()
            if pygame.mixer.get_init():
                pygame.mixer.music.set_volume(vol)
        except Exception:
            pass

    def _toggle_play_pause(self):
        if self.playing and not self.stop_requested:
            self._on_pause() if not self.paused else self._on_resume()
        elif not self.playing and self.songs:
            self._on_play()

    def _on_play(self):
        if not self.songs:
            messagebox.showerror("Error", "No songs in songs.json")
            return
        sid = self.song_var.get()
        if not sid:
            messagebox.showerror("Error", "Select a song")
            return
        try:
            start_at = float(self.start_var.get())
        except ValueError:
            start_at = 0.0

        self.current_song = get_song(sid)
        if not self.current_song:
            messagebox.showerror("Error", f"Song '{sid}' not found")
            return
        if self.playback_thread and self.playback_thread.is_alive():
            return

        self.playing = True
        self.paused = False
        self.stop_requested = False
        self.play_btn.config(state=tk.DISABLED)
        self.pause_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.NORMAL)
        self.text.delete(1.0, tk.END)
        self.status_var.set("Playing...")

        char_delay = get_char_delay(self.current_song, None)
        self.playback_thread = threading.Thread(
            target=self._run_playback,
            args=(start_at, char_delay, self.theme_var.get()),
        )
        self.playback_thread.daemon = True
        self.playback_thread.start()

    def _on_pause(self):
        if not self.playing or self.paused:
            return
        self.paused = True
        pygame.mixer.music.pause()
        self.pause_btn.config(text="▶ Resume", command=self._on_resume)
        self.status_var.set("Paused")

    def _on_resume(self):
        if not self.paused:
            return
        self.paused = False
        pygame.mixer.music.unpause()
        self.pause_btn.config(text="⏸ Pause", command=self._on_pause)
        self.status_var.set("Playing...")

    def _on_stop(self):
        self.stop_requested = True
        self.playing = False
        self.paused = False
        self.status_var.set("Stopped")

    def _run_playback(self, start_at, char_delay, theme):
        song = self.current_song
        audio_path = get_audio_path(song, PROJECT_ROOT)
        lyrics = song["lyrics"]
        line_delay = get_line_delay(song)

        if not os.path.exists(audio_path):
            self.root.after(0, lambda: messagebox.showerror("Error", "Audio file not found"))
            self.root.after(0, self._reset_ui)
            return

        pygame.mixer.init()
        try:
            pygame.mixer.music.load(audio_path)
            pygame.mixer.music.set_volume(self.volume_var.get())
            pygame.mixer.music.play(start=start_at)
        except pygame.error:
            self.root.after(0, lambda: messagebox.showerror("Error", "Could not load audio"))
            self.root.after(0, self._reset_ui)
            return

        theme_colors = THEMES.get(theme, [])
        color_index = 0

        def stop_check():
            return self.stop_requested

        for ts, line, entry_delay in iter_lyrics(lyrics, start_at, line_delay, stop_check):
            if self.stop_requested:
                break
            if self.paused:
                while self.paused and not self.stop_requested:
                    time.sleep(0.1)
                if self.stop_requested:
                    break

            if line.strip():
                for i, char in enumerate(line):
                    if self.stop_requested:
                        break
                    if self.paused:
                        while self.paused and not self.stop_requested:
                            time.sleep(0.05)
                    if self.stop_requested:
                        break
                    if theme_colors and theme != "plain":
                        cname = theme_colors[(color_index + i) % len(theme_colors)]
                        hex_color = THEME_COLORS_HEX.get(cname, DEFAULT_TEXT_COLOR)
                        self.root.after(0, lambda c=char, h=hex_color: self._append_char(c, h))
                    else:
                        self.root.after(0, lambda c=char: self._append_char(c, None))
                    time.sleep(char_delay)
                color_index += 1
                self.root.after(0, lambda: self._append_text("\n"))
                if entry_delay > 0:
                    time.sleep(entry_delay)
            else:
                self.root.after(0, lambda: self._append_text("\n"))
                if entry_delay > 0:
                    time.sleep(entry_delay)

        if self.stop_requested:
            pygame.mixer.music.stop()
        else:
            while pygame.mixer.music.get_busy() and not self.stop_requested:
                time.sleep(0.1)
            if self.stop_requested:
                pygame.mixer.music.stop()

        self.root.after(0, self._reset_ui)

    def _append_text(self, s):
        self.text.insert(tk.END, s)
        self.text.see(tk.END)

    def _append_char(self, c, color_hex=None):
        if color_hex:
            tag = f"c_{color_hex}"
            self.text.tag_config(tag, foreground=color_hex)
            self.text.insert(tk.END, c, tag)
        else:
            self.text.insert(tk.END, c)
        self.text.see(tk.END)

    def _reset_ui(self):
        self.playing = False
        self.paused = False
        self.play_btn.config(state=tk.NORMAL)
        self.pause_btn.config(text="⏸ Pause", command=self._on_pause, state=tk.DISABLED)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_var.set("Ready")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = LyricStreamGUI()
    app.run()
