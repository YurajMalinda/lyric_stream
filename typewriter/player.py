"""
Playback engine: lyric timing, iter_lyrics, audio path, char/line delay.
"""

import os
import time
from typing import Callable, Optional

DEFAULT_CHAR_DELAY = 0.03
DEFAULT_LINE_DELAY = 0.0


def parse_lyric_entry(entry: list, default_line_delay: float = 0.0) -> tuple:
    """Parse [timestamp, line] or [timestamp, line, delay] from songs.json."""
    if len(entry) == 3:
        return float(entry[0]), entry[1], float(entry[2])
    return float(entry[0]), entry[1], default_line_delay


def iter_lyrics(
    lyrics: list,
    start_at: float,
    line_delay: float,
    stop_check: Optional[Callable[[], bool]] = None,
):
    """Yield (timestamp, line, entry_delay) when each line is due based on song position."""
    start_time = time.time()

    for entry in lyrics:
        if stop_check and stop_check():
            return

        ts, line, entry_delay = parse_lyric_entry(entry, line_delay)

        if ts < start_at:
            continue

        elapsed = time.time() - start_time
        song_position = start_at + elapsed
        wait = ts - song_position

        if wait > 0:
            sleep_interval = 0.05
            while wait > 0 and (not stop_check or not stop_check()):
                time.sleep(min(sleep_interval, wait))
                elapsed = time.time() - start_time
                song_position = start_at + elapsed
                wait = ts - song_position

        if stop_check and stop_check():
            return

        yield ts, line, entry_delay


def get_audio_path(song: dict, project_root: str) -> str:
    """Return full path to the song's audio file."""
    return os.path.join(project_root, song["audio"])


def get_char_delay(song: dict, override: Optional[float] = None) -> float:
    """Return char delay, using override or song's default."""
    return override if override is not None else song.get("char_delay", DEFAULT_CHAR_DELAY)


def get_line_delay(song: dict) -> float:
    """Return line delay from song config."""
    return song.get("line_delay", DEFAULT_LINE_DELAY)
