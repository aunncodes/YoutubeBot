import json
import random
import re
import time

from youtubebot.cards.reddit_title_card import RedditTitleCardBuilder
from youtubebot.models import RenderRequest, VideoResult
from youtubebot.rendering.ffmpeg import FFmpegRenderer
from youtubebot.sources.reddit import RedditStorySource
from youtubebot.state import UsedContentStore
from youtubebot.subtitles.ass import AssSubtitleBuilder
from youtubebot.text import build_reddit_narration, clean_reddit_text
from youtubebot.narration_text import expand_reddit_acronyms
from youtubebot.upload_metadata import make_upload_metadata
from youtubebot.video_types.base import VideoType


def slug(value, limit=60):
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-").lower()
    return value[:limit].rstrip("-") or "reddit-story"


def make_narrator(settings):
    if settings.tts_provider == "gemini":
        from youtubebot.narration.gemini import GeminiNarrator

        return GeminiNarrator(settings)

    if settings.tts_provider == "chatterbox":
        from youtubebot.narration.chatterbox import ChatterboxNarrator

        return ChatterboxNarrator(settings)

    raise ValueError(f"Unknown TTS provider: {settings.tts_provider}")


class RedditStoryVideo(VideoType):
    def __init__(self, settings):
        self.settings = settings
        self.used_store = UsedContentStore(settings.state_path)
        self.source = RedditStorySource(settings, self.used_store)
        self.narrator = make_narrator(settings)
        self.subtitle_builder = AssSubtitleBuilder(settings)
        self.title_card_builder = RedditTitleCardBuilder(settings)
        self.renderer = FFmpegRenderer(settings)

    def create(self):
        item = self.source.fetch()
        self.used_store.add(item.source_id)

        original_narration = build_reddit_narration(
            item.title,
            item.body,
            self.settings.outro_text,
        )
        narration_text = expand_reddit_acronyms(original_narration)
        spoken_title = expand_reddit_acronyms(
            clean_reddit_text(item.title).rstrip(".?!")
        )

        run_name = (
            f"{time.strftime('%Y%m%d-%H%M%S')}-"
            f"{item.source_id}-{slug(item.title)}"
        )
        run_dir = self.settings.output_dir / run_name
        work_dir = run_dir / "work"
        work_dir.mkdir(parents=True)

        narration = self.narrator.synthesize(narration_text, work_dir)
        subtitles = self.subtitle_builder.build(narration, work_dir, spoken_title)
        title_card = self.title_card_builder.build(item.title, work_dir)
        subscribe_button = self.settings.icon_dir / "subscribe-button.png"
        if not subscribe_button.exists():
            raise FileNotFoundError(f"Missing subscribe button asset: {subscribe_button}")
        background = self.pick_background()
        music = self.pick_music()
        video_path = run_dir / f"{run_name}.mp4"
        metadata_path = run_dir / "metadata.json"

        metadata = make_upload_metadata(
            item,
            narration_text,
            background,
            music,
            self.settings,
        )
        metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

        self.renderer.render(
            RenderRequest(
                background,
                narration.audio_path,
                subtitles.path,
                video_path,
                music,
                title_card,
                subtitles.title_start,
                subtitles.title_end,
                subscribe_button,
                subtitles.outro_start,
                subtitles.outro_end,
            )
        )

        return VideoResult(video_path, item.url, metadata["title"], metadata_path)

    def pick_background(self):
        candidates = sorted(self.settings.reddit_background_dir.glob("*.mp4"))
        if not candidates:
            raise RuntimeError(
                f"No background MP4 files found in {self.settings.reddit_background_dir}"
            )
        return random.choice(candidates)

    def pick_music(self):
        extensions = {".mp3", ".wav", ".m4a", ".aac", ".ogg", ".flac"}
        candidates = []

        for path in self.settings.music_dir.glob("*"):
            if path.is_file() and path.suffix.casefold() in extensions:
                candidates.append(path)

        if not candidates:
            print(f"No music found in {self.settings.music_dir}. Using narration only.")
            return None

        return random.choice(candidates)
