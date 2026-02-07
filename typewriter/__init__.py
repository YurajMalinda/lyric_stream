"""
LyricStream - Core package.

Exports:
- display: typewriter effect, themes, clear_screen
- songs_loader: load_songs, get_song, list_songs
- player: iter_lyrics, parse_lyric_entry, get_audio_path, get_char_delay, get_line_delay
"""

__version__ = "1.0.0"

from .display import (
    typewriter_print_with_theme,
    clear_screen,
    THEMES,
    get_theme_list,
)
from .songs_loader import load_songs, get_song, list_songs
from .player import (
    iter_lyrics,
    parse_lyric_entry,
    get_audio_path,
    get_char_delay,
    get_line_delay,
)

__all__ = [
    "typewriter_print_with_theme",
    "clear_screen",
    "THEMES",
    "get_theme_list",
    "load_songs",
    "get_song",
    "list_songs",
    "iter_lyrics",
    "parse_lyric_entry",
    "get_audio_path",
    "get_char_delay",
    "get_line_delay",
]
