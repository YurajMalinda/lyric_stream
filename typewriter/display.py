"""
Typewriter lyric effect: character-by-character output with optional color themes.
"""

import os
import sys
import time

_ANSI = {
    "reset": "\033[0m",
    "bold": "\033[1m",
    "red": "\033[91m",
    "green": "\033[92m",
    "yellow": "\033[93m",
    "blue": "\033[94m",
    "magenta": "\033[95m",
    "cyan": "\033[96m",
    "white": "\033[97m",
}

THEMES = {
    "plain": [],
    "colorful": ["cyan", "green", "yellow", "magenta", "blue"],
    "warm": ["yellow", "red", "magenta"],
    "cool": ["cyan", "blue"],
}


def clear_screen() -> None:
    """Clear the terminal (cls on Windows, clear on Unix)."""
    os.system("cls" if os.name == "nt" else "clear")


def typewriter_print_with_theme(
    text: str, delay: float, theme: str, color_index: int = 0, end: str = "\n"
) -> int:
    """Print text with typewriter effect and theme-based color cycling."""
    if theme == "plain" or theme not in THEMES or not THEMES[theme]:
        for char in text:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(delay)
        sys.stdout.write(end)
        sys.stdout.flush()
        return 0

    colors = THEMES[theme]
    color = _ANSI.get(colors[color_index % len(colors)], "")
    for char in text:
        sys.stdout.write(f"{color}{char}{_ANSI['reset']}")
        sys.stdout.flush()
        time.sleep(delay)
    sys.stdout.write(end)
    sys.stdout.flush()
    return color_index + 1


def get_theme_list() -> list:
    """Return available theme names."""
    return list(THEMES.keys())
