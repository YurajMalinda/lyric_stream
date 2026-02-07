"""
Load songs from songs.json. Structure: songs[{id, title, artist, audio, lyrics, char_delay, line_delay}].
"""

import json
import os
from typing import Optional

DEFAULT_SONGS_FILE = "songs.json"


def load_songs(songs_file: str = None) -> list:
    """Load songs from JSON. Uses songs.json in project root if songs_file is None."""
    path = songs_file or _find_songs_file()
    if not path or not os.path.exists(path):
        return []

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    songs = data.get("songs", [])
    for s in songs:
        s.setdefault("char_delay", 0.03)
        s.setdefault("line_delay", 0.0)
        s.setdefault("artist", "")
    return songs


def get_song(song_id: str, songs_file: str = None) -> Optional[dict]:
    """Get song by ID, or None if not found."""
    songs = load_songs(songs_file)
    for s in songs:
        if s.get("id") == song_id:
            return s
    return None


def list_songs(songs_file: str = None) -> list:
    """Return [(id, title), ...] for all songs."""
    songs = load_songs(songs_file)
    return [(s["id"], s.get("title", s["id"])) for s in songs]


def _find_songs_file() -> Optional[str]:
    """Find songs.json in project root."""
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(base, DEFAULT_SONGS_FILE)
    return path if os.path.exists(path) else None
