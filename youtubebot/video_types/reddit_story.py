import json
import random
import re
import time

from youtubebot.cards.reddit_title_card import RedditTitleCardBuilder
from youtubebot.models import RenderRequest, VideoResult
from youtubebot.narration.chatterbox import ChatterboxNarrator
from youtubebot.rendering.ffmpeg import FFmpegRenderer
from youtubebot.sources.reddit import RedditStorySource
from youtubebot.state import UsedContentStore
from youtubebot.subtitles.ass import AssSubtitleBuilder
from youtubebot.text import build_reddit_narration
from youtubebot.upload_metadata import make_upload_metadata
from youtubebot.video_types.base import VideoType


def slug(value, limit=60):
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-").lower()
    return value[:limit].rstrip("-") or "reddit-story"


class RedditStoryVideo(VideoType):
    def __init__(self, settings):
        self.settings = settings
        self.used_store = UsedContentStore(settings.state_path)
        self.source = RedditStorySource(settings, self.used_store)
        self.narrator = ChatterboxNarrator(settings)
        self.subtitle_builder = AssSubtitleBuilder(settings)
        self.title_card_builder = RedditTitleCardBuilder(settings)
        self.renderer = FFmpegRenderer(settings)

    def create(self):
        item = self.source.fetch()
        self.used_store.add(item.source_id)

        narration_text = build_reddit_narration(
            item.title,
            item.body,
            self.settings.outro_text,
        )
        run_name = (
            f"{time.strftime('%Y%m%d-%H%M%S')}-"
            f"{item.source_id}-{slug(item.title)}"
        )
        run_dir = self.settings.output_dir / run_name
        work_dir = run_dir / "work"
        work_dir.mkdir(parents=True)

        narration = self.narrator.synthesize(narration_text, work_dir)
        subtitles = self.subtitle_builder.build(narration, work_dir, item.title)
        title_card = self.title_card_builder.build(item.title, work_dir)
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
