#!/usr/bin/env python3
"""
Record lyric timestamps for new songs. Outputs JSON ready to paste into songs.json.
No external dependencies. Run: python timestamp_helper.py
"""

import json
import time
import sys


def main() -> None:
    """Run the interactive timestamp recording session."""
    print("=" * 60)
    print("TIMESTAMP HELPER")
    print("=" * 60)
    print()
    print("Records when each lyric line starts. Use the output to add songs to songs.json.")
    print()
    print("Steps:")
    print("  1. Open your song in a music player (VLC, Spotify, etc.)")
    print("  2. Start playing the song")
    print("  3. Press ENTER when each lyric line starts")
    print("  4. Type the lyric line and press ENTER")
    print("  5. Press Ctrl+C when done")
    print()

    title = input("Song title (e.g. 'My Song - Artist'): ").strip() or "Untitled"
    audio = input("Audio filename (e.g. song.mp3): ").strip() or "song.mp3"
    song_id = input("Song ID for songs.json (e.g. my_song): ").strip() or "song_1"

    input("\nPress ENTER when ready to start timing...")

    timestamps = []
    start_time = time.time()

    print("\nTimer started. Press ENTER when each lyric line begins...")
    print("(Press Ctrl+C when finished)\n")

    try:
        while True:
            input()
            current_time = time.time() - start_time
            lyric = input(f"[{current_time:.2f}s] Enter lyric line: ").strip()

            if lyric:
                timestamps.append((current_time, lyric))
                print(f"Added: ({current_time:.2f}, \"{lyric}\")\n")
            else:
                timestamps.append((current_time, ""))
                print(f"Added empty line at {current_time:.2f}s\n")

    except KeyboardInterrupt:
        pass

    if timestamps:
        lyrics = [[0.0, f"🎵 {title} 🎵"], [2.0, ""]]
        for ts, lyric in timestamps:
            lyrics.append([round(ts, 2), lyric])

        song_entry = {
            "id": song_id,
            "title": title,
            "artist": "",
            "audio": audio,
            "lyrics": lyrics,
            "char_delay": 0.16,
            "line_delay": 0.0,
        }

        print("\n" + "=" * 60)
        print("SONG ENTRY - Add to songs.json")
        print("=" * 60)
        print(json.dumps(song_entry, indent=2, ensure_ascii=False))
        print()
        print("Copy the above JSON and add it to the 'songs' array in songs.json")
        print()
    else:
        print("\nNo timestamps collected.")


if __name__ == "__main__":
    main()
