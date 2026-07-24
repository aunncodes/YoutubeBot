# YouTube Video Bot

A small Python project to automatically create Youtube Videos like reddit stories.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Fill in the Reddit credentials in `.env`.

On macOS, install FFmpeg:

```bash
brew install ffmpeg-full
```

## Assets

Add one or more background videos here:

```text
assets/backgrounds/reddit/
```

Add quiet ambient music here:

```text
assets/music/
```

Supported music formats are MP3, WAV, M4A, AAC, OGG, and FLAC. The renderer loops a randomly selected track and puts it beneath the narration.

If `assets/music/` is empty, the video will render without music.

## Run

```bash
python main.py reddit-story
```

The generated MP4 and metadata are written under `output/<run>/`.
