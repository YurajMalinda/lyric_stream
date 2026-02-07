# LyricStream 🎵

Python app that plays audio with synchronized typewriter-style lyrics. Lyrics appear character by character, timed to the music. Supports multiple songs, themes, and both CLI and GUI.

## Features

- **Typewriter effect** – Lyrics appear one character at a time
- **Synced with audio** – Lyrics display at the correct moment in the song
- **songs.json** – All songs defined in one JSON file
- **Typing speed per song** – `char_delay` in each song config
- **Themes** – plain, colorful, warm, cool
- **CLI & GUI** – Terminal player and graphical interface

## Project Structure

```
lyricstream/
├── play.py              # CLI player
├── gui.py               # GUI player
├── songs.json           # Song definitions (audio, lyrics, timestamps)
├── timestamp_helper.py  # Record timestamps when adding new songs
├── run.sh               # Run CLI (Linux/macOS)
├── run_gui.sh           # Run GUI (Linux/macOS)
├── typewriter/
│   ├── __init__.py
│   ├── display.py       # Typewriter effect, themes
│   ├── songs_loader.py  # Load songs from JSON
│   └── player.py       # Playback timing logic
├── requirements.txt
└── README.md
```

## Quick Start

```bash
python3 -m venv .venv
source .venv/bin/activate   # Linux/macOS; Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

**CLI:**

```bash
./run.sh
# or
python play.py
```

**GUI:**

```bash
./run_gui.sh
# or
python gui.py
```

On Linux, if the GUI fails with "tkinter is not available":

```bash
sudo apt install python3-tk
```

## Troubleshooting

**"pygame is not installed"** – Make sure the venv is activated and dependencies are installed. If `pip install` fails, use the venv's pip explicitly:

```bash
.venv/bin/pip install -r requirements.txt   # Linux/macOS
.venv\Scripts\pip install -r requirements.txt   # Windows
```

**"externally-managed-environment"** – This happens when `pip` resolves to the system Python instead of the venv. Use the venv's pip path above, or ensure the venv is activated before running `pip`.

**Broken venv after moving/copying the project** – The venv stores absolute paths. If you moved the project, recreate it:

```bash
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate   # Linux/macOS; Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## songs.json Format

The project includes an example song (Mama Pathuwe by Minura Halwathura) with lyrics and timelines already created. Add your own songs using the format below.

```json
{
  "songs": [
    {
      "id": "mama_pathuwe",
      "title": "Mama Pathuwe - Minura Halwathura",
      "artist": "Minura Halwathura",
      "audio": "Mama Pathuwe - Minura Halwathura.mp3",
      "lyrics": [
        [0.0, "🎵 Song Title 🎵"],
        [2.0, ""],
        [18.9, "First lyric line"],
        [25.9, "Second lyric line", 0.5]
      ],
      "char_delay": 0.16,
      "line_delay": 0.0
    }
  ]
}
```

| Field        | Description                                                                            |
| ------------ | -------------------------------------------------------------------------------------- |
| `id`         | Unique identifier                                                                      |
| `title`      | Display title                                                                          |
| `artist`     | Artist name (optional)                                                                 |
| `audio`      | Filename of the audio file (MP3, WAV, or OGG)                                          |
| `lyrics`     | Lyrics with timelines for that song: `[timestamp, line]` or `[timestamp, line, delay]` |
| `char_delay` | Typing speed in seconds per character (lower = faster)                                 |
| `line_delay` | Pause after each line in seconds (0 = no pause)                                        |

Lyric entries:

- `[timestamp, "line"]` – Line at timestamp, uses song's `line_delay`
- `[timestamp, "line", delay]` – Line at timestamp, custom delay after

## CLI Usage

```bash
python play.py                    # Play first song
python play.py mama_pathuwe       # Play specific song
python play.py --list             # List available songs
python play.py --start 30         # Start at 30 seconds
python play.py --theme colorful    # Colored output
```

| Option    | Short | Description                 |
| --------- | ----- | --------------------------- |
| `--start` | `-s`  | Start position in seconds   |
| `--theme` | `-t`  | plain, colorful, warm, cool |
| `--list`  | `-l`  | List songs and exit         |

## GUI

- Song selection, theme, font, size
- Start position, volume
- Play / Pause / Stop (Space, Escape shortcuts)
- Typing speed from song's `char_delay`

## Themes

| Theme      | Description                        |
| ---------- | ---------------------------------- |
| `plain`    | No colors (default)                |
| `colorful` | Cyan, green, yellow, magenta, blue |
| `warm`     | Yellow, red, magenta               |
| `cool`     | Cyan, blue                         |

## Adding a New Song

1. Place your audio file in the project folder.
2. Run: `python timestamp_helper.py`
3. Enter song title, audio filename, and song ID.
4. Start your song in a music player (VLC, Spotify, etc.).
5. Press ENTER when each lyric line starts, then type the lyric.
6. Press Ctrl+C when done.
7. Copy the printed JSON into the `songs` array in `songs.json`.

## Requirements

- Python 3.8+
- pygame (audio)
- tkinter (GUI; usually included; on Ubuntu/Debian: `python3-tk`)
- ttkbootstrap (optional; dark theme; falls back to standard tkinter)

## Platform Support

Works on **Windows**, **macOS**, and **Linux**.

| Platform    | Notes                                                                                 |
| ----------- | ------------------------------------------------------------------------------------- |
| **Linux**   | `run.sh` and `run_gui.sh` work. GUI: `sudo apt install python3-tk` if needed.         |
| **macOS**   | `run.sh` and `run_gui.sh` work.                                                       |
| **Windows** | Use `python play.py` or `python gui.py`. Activate venv with `.venv\Scripts\activate`. |

## Tips

- **Typing speed**: `char_delay = 0.01` for fast songs, `0.1–0.2` for slow, dramatic effect.
- **Syncing**: If a line appears too early, increase its timestamp; if too late, decrease it.
- **Recording**: Use a terminal recorder (asciinema, OBS) to capture output for videos.

## Publishing / Adding Your Own Songs

Audio files (`*.mp3`, `*.wav`, `*.ogg`) are excluded from version control via `.gitignore`. When you publish (e.g. to GitHub), your audio files stay local and are not uploaded.

To use the app with your own songs:

1. Place your audio file in the project folder
2. Run `python timestamp_helper.py` to record timestamps
3. Add the output to `songs.json`, or replace the existing entries

## License

MIT License – see [LICENSE](LICENSE) for details. Ensure you have rights to any audio and lyrics you use.
