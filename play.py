#!/usr/bin/env python3
"""
LyricStream - CLI.

Plays audio with synced typewriter lyrics. Typing speed from songs.json.
Usage: python play.py [song_id] [--start 0] [--theme plain] | python play.py --list
"""

import os
import sys
import time
import argparse

try:
    import pygame
except ImportError:
    print("Error: pygame is not installed.")
    print("Run: source .venv/bin/activate && pip install pygame")
    sys.exit(1)

from typewriter.display import typewriter_print_with_theme, clear_screen, get_theme_list
from typewriter.songs_loader import load_songs, get_song, list_songs
from typewriter.player import iter_lyrics, get_audio_path, get_char_delay, get_line_delay


def _project_root() -> str:
    """Return the project root directory (where play.py lives)."""
    return os.path.dirname(os.path.abspath(__file__))


def play_song(song: dict, start_at: float = 0.0, theme: str = "plain") -> None:
    """Play a song with synced typewriter lyrics. Typing speed from song's char_delay."""
    root = _project_root()
    audio_path = get_audio_path(song, root)

    if not os.path.exists(audio_path):
        print(f"Error: Audio file '{song['audio']}' not found.")
        sys.exit(1)

    lyrics = song["lyrics"]
    delay = get_char_delay(song, None)
    line_delay = get_line_delay(song)

    clear_screen()
    pygame.mixer.init()

    try:
        pygame.mixer.music.load(audio_path)
        pygame.mixer.music.play(start=start_at)

        print("=" * 50)
        print("Playing:", song.get("title", song["audio"]))
        print("=" * 50)
        print()

        color_index = 0
        for ts, line, entry_delay in iter_lyrics(lyrics, start_at, line_delay):
            if line.strip():
                color_index = typewriter_print_with_theme(
                    line, delay, theme, color_index
                )
                if entry_delay > 0:
                    time.sleep(entry_delay)
            else:
                print()
                if entry_delay > 0:
                    time.sleep(entry_delay)

        print("\n" + "=" * 50)
        print("Song playing... (Press Ctrl+C to stop)")
        print("=" * 50)

        while pygame.mixer.music.get_busy():
            time.sleep(0.1)

        print("\n🎉 Song finished! 🎉")

    except pygame.error as e:
        print(f"Error playing audio: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nStopped by user")
        pygame.mixer.music.stop()
        sys.exit(0)


def main() -> None:
    """Parse CLI arguments and run the player."""
    parser = argparse.ArgumentParser(
        description="LyricStream - Synced lyrics with audio"
    )
    parser.add_argument(
        "song",
        nargs="?",
        default=None,
        help="Song ID from songs.json. Omitted = play first song.",
    )
    parser.add_argument(
        "--start", "-s",
        type=float,
        default=0.0,
        help="Start position in seconds (default: 0)",
    )
    parser.add_argument(
        "--theme", "-t",
        choices=get_theme_list(),
        default="plain",
        help="Display theme (default: plain)",
    )
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="List available songs and exit",
    )
    args = parser.parse_args()

    if args.list:
        songs = list_songs()
        if not songs:
            print("No songs found. Add songs to songs.json")
            sys.exit(1)
        print("Available songs:")
        for sid, title in songs:
            print(f"  {sid}: {title}")
        return

    songs = load_songs()
    if not songs:
        print("Error: No songs in songs.json")
        sys.exit(1)

    song_id = args.song or songs[0]["id"]
    song = get_song(song_id)
    if not song:
        print(f"Error: Song '{song_id}' not found.")
        print("Use --list to see available songs.")
        sys.exit(1)

    play_song(song, start_at=args.start, theme=args.theme)


if __name__ == "__main__":
    main()
