import os
from pathlib import Path


def get_int(name, default):
    return int(os.getenv(name, default))


def get_float(name, default):
    return float(os.getenv(name, default))


def get_bool(name, default):
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().casefold() in {"1", "true", "yes", "on"}


class Settings:
    def __init__(
        self,
        project_root,
        reddit_client_id,
        reddit_client_secret,
        reddit_user_agent,
        tts_provider,
        gemini_api_key,
        gemini_tts_model,
        gemini_tts_voice,
        gemini_tts_style,
        chatterbox_device,
        chatterbox_voice_path,
        chatterbox_exaggeration,
        chatterbox_cfg_weight,
        whisper_model,
        whisper_device,
        reddit_subreddits,
        reddit_listing_limit,
        reddit_selection_pool,
        reddit_max_age_hours,
        reddit_min_score,
        reddit_min_comments,
        reddit_min_upvote_ratio,
        reddit_min_words,
        reddit_max_words,
        video_max_duration,
        video_duration_safety,
        narration_estimated_wpm,
        video_width,
        video_height,
        video_fps,
        video_crf,
        video_preset,
        video_fade_seconds,
        music_volume,
        narration_normalize,
        narration_loudness,
        narration_loudness_range,
        narration_true_peak,
        outro_text,
        subscribe_text,
        outro_hold_seconds,
        subtitle_max_duration,
        subtitle_min_duration,
        subtitle_hard_max_words,
        subtitle_max_lines,
        subtitle_target_fill,
        subtitle_min_fill,
        subtitle_side_margin,
        subtitle_font,
        subtitle_font_size,
        subtitle_outline,
        subtitle_shadow,
        subtitle_pop_ms,
        channel_name,
        title_card_hold_seconds,
    ):
        self.project_root = project_root
        self.reddit_client_id = reddit_client_id
        self.reddit_client_secret = reddit_client_secret
        self.reddit_user_agent = reddit_user_agent
        self.tts_provider = tts_provider
        self.gemini_api_key = gemini_api_key
        self.gemini_tts_model = gemini_tts_model
        self.gemini_tts_voice = gemini_tts_voice
        self.gemini_tts_style = gemini_tts_style
        self.chatterbox_device = chatterbox_device
        self.chatterbox_voice_path = chatterbox_voice_path
        self.chatterbox_exaggeration = chatterbox_exaggeration
        self.chatterbox_cfg_weight = chatterbox_cfg_weight
        self.whisper_model = whisper_model
        self.whisper_device = whisper_device
        self.reddit_subreddits = reddit_subreddits
        self.reddit_listing_limit = reddit_listing_limit
        self.reddit_selection_pool = reddit_selection_pool
        self.reddit_max_age_hours = reddit_max_age_hours
        self.reddit_min_score = reddit_min_score
        self.reddit_min_comments = reddit_min_comments
        self.reddit_min_upvote_ratio = reddit_min_upvote_ratio
        self.reddit_min_words = reddit_min_words
        self.reddit_max_words = reddit_max_words
        self.video_max_duration = video_max_duration
        self.video_duration_safety = video_duration_safety
        self.narration_estimated_wpm = narration_estimated_wpm
        self.video_width = video_width
        self.video_height = video_height
        self.video_fps = video_fps
        self.video_crf = video_crf
        self.video_preset = video_preset
        self.video_fade_seconds = video_fade_seconds
        self.music_volume = music_volume
        self.narration_normalize = narration_normalize
        self.narration_loudness = narration_loudness
        self.narration_loudness_range = narration_loudness_range
        self.narration_true_peak = narration_true_peak
        self.outro_text = outro_text
        self.subscribe_text = subscribe_text
        self.outro_hold_seconds = outro_hold_seconds
        self.subtitle_max_duration = subtitle_max_duration
        self.subtitle_min_duration = subtitle_min_duration
        self.subtitle_hard_max_words = subtitle_hard_max_words
        self.subtitle_max_lines = subtitle_max_lines
        self.subtitle_target_fill = subtitle_target_fill
        self.subtitle_min_fill = subtitle_min_fill
        self.subtitle_side_margin = subtitle_side_margin
        self.subtitle_font = subtitle_font
        self.subtitle_font_size = subtitle_font_size
        self.subtitle_outline = subtitle_outline
        self.subtitle_shadow = subtitle_shadow
        self.subtitle_pop_ms = subtitle_pop_ms
        self.channel_name = channel_name
        self.title_card_hold_seconds = title_card_hold_seconds
        self.reddit_background_dir = project_root / "assets" / "backgrounds" / "reddit"
        self.music_dir = project_root / "assets" / "music"
        self.icon_dir = project_root / "assets" / "icons"
        self.output_dir = project_root / "output"
        self.state_path = project_root / "data" / "used_reddit_posts.json"


def choose_chatterbox_device(value):
    if value:
        return value

    try:
        import torch

        if torch.backends.mps.is_available():
            return "mps"
    except Exception:
        pass

    return "cpu"


def normalize_path(value, root):
    if not value:
        return None

    path = Path(value).expanduser()

    if not path.is_absolute():
        path = root / path

    return path.resolve()


def load_settings():
    from dotenv import load_dotenv

    root = Path.cwd().resolve()
    load_dotenv(root / ".env", override=True)

    subreddits = []
    subreddit_text = os.getenv(
        "REDDIT_SUBREDDITS",
        "AITAH,AmItheAsshole,TrueOffMyChest,pettyrevenge,MaliciousCompliance",
    )

    for value in subreddit_text.split(","):
        value = value.strip()
        if value.startswith("r/"):
            value = value[2:]
        if value:
            subreddits.append(value)

    missing = []
    for name in ("REDDIT_CLIENT_ID", "REDDIT_CLIENT_SECRET", "REDDIT_USER_AGENT"):
        if not os.getenv(name, "").strip():
            missing.append(name)

    if missing:
        raise ValueError("Missing Reddit settings: " + ", ".join(missing))

    tts_provider = os.getenv("TTS_PROVIDER", "gemini").strip().casefold()
    if tts_provider not in {"gemini", "chatterbox"}:
        raise ValueError("TTS_PROVIDER must be gemini or chatterbox")

    chatterbox_voice_path = normalize_path(
        os.getenv("CHATTERBOX_VOICE_PATH", "").strip(),
        root,
    )

    return Settings(
        project_root=root,
        reddit_client_id=os.getenv("REDDIT_CLIENT_ID").strip(),
        reddit_client_secret=os.getenv("REDDIT_CLIENT_SECRET").strip(),
        reddit_user_agent=os.getenv("REDDIT_USER_AGENT").strip(),
        tts_provider=tts_provider,
        gemini_api_key=os.getenv("GEMINI_API_KEY", "").strip(),
        gemini_tts_model=os.getenv(
            "GEMINI_TTS_MODEL",
            "gemini-3.1-flash-tts-preview",
        ).strip(),
        gemini_tts_voice=os.getenv("GEMINI_TTS_VOICE", "Achird").strip(),
        gemini_tts_style=os.getenv(
            "GEMINI_TTS_STYLE",
            "Speak in one consistent, upbeat, confident voice from start to finish. "
            "Use a clear projected volume, a friendly optimistic tone, and a natural "
            "medium-fast pace. Keep the delivery steady. Do not whisper, become breathy, "
            "act out characters, dramatize emotional moments, or change pitch and speed "
            "for emphasis. Use only light natural emphasis and short pauses at punctuation. "
            "Read the transcript exactly as written.",
        ).strip(),
        chatterbox_device=choose_chatterbox_device(
            os.getenv("CHATTERBOX_DEVICE", "").strip()
        ),
        chatterbox_voice_path=chatterbox_voice_path,
        chatterbox_exaggeration=get_float("CHATTERBOX_EXAGGERATION", 0.65),
        chatterbox_cfg_weight=get_float("CHATTERBOX_CFG_WEIGHT", 0.35),
        whisper_model=os.getenv("WHISPER_MODEL", "tiny.en").strip(),
        whisper_device=os.getenv("WHISPER_DEVICE", "cpu").strip(),
        reddit_subreddits=subreddits,
        reddit_listing_limit=get_int("REDDIT_LISTING_LIMIT", 100),
        reddit_selection_pool=max(1, get_int("REDDIT_SELECTION_POOL", 20)),
        reddit_max_age_hours=get_float("REDDIT_MAX_AGE_HOURS", 168),
        reddit_min_score=get_int("REDDIT_MIN_SCORE", 100),
        reddit_min_comments=get_int("REDDIT_MIN_COMMENTS", 10),
        reddit_min_upvote_ratio=get_float("REDDIT_MIN_UPVOTE_RATIO", 0.70),
        reddit_min_words=get_int("REDDIT_MIN_WORDS", 80),
        reddit_max_words=get_int("REDDIT_MAX_WORDS", 700),
        video_max_duration=max(1.0, get_float("VIDEO_MAX_DURATION", 180.0)),
        video_duration_safety=max(0.0, get_float("VIDEO_DURATION_SAFETY", 8.0)),
        narration_estimated_wpm=max(1.0, get_float("NARRATION_ESTIMATED_WPM", 165.0)),
        video_width=get_int("VIDEO_WIDTH", 1080),
        video_height=get_int("VIDEO_HEIGHT", 1920),
        video_fps=get_int("VIDEO_FPS", 30),
        video_crf=get_int("VIDEO_CRF", 20),
        video_preset=os.getenv("VIDEO_PRESET", "medium").strip(),
        video_fade_seconds=max(0.1, get_float("VIDEO_FADE_SECONDS", 1.0)),
        music_volume=max(0.0, get_float("MUSIC_VOLUME", 0.10)),
        narration_normalize=get_bool("NARRATION_NORMALIZE", True),
        narration_loudness=get_float("NARRATION_LOUDNESS", -14.0),
        narration_loudness_range=max(1.0, get_float("NARRATION_LOUDNESS_RANGE", 5.0)),
        narration_true_peak=get_float("NARRATION_TRUE_PEAK", -1.5),
        outro_text=os.getenv(
            "OUTRO_TEXT",
            "So what do you think? Comment down below!",
        ).strip(),
        subscribe_text=os.getenv("SUBSCRIBE_TEXT", "SUBSCRIBE").strip(),
        outro_hold_seconds=max(0.0, get_float("OUTRO_HOLD_SECONDS", 1.4)),
        subtitle_max_duration=max(0.4, get_float("SUBTITLE_MAX_DURATION", 2.35)),
        subtitle_min_duration=max(0.0, get_float("SUBTITLE_MIN_DURATION", 0.55)),
        subtitle_hard_max_words=max(2, get_int("SUBTITLE_HARD_MAX_WORDS", 10)),
        subtitle_max_lines=max(1, get_int("SUBTITLE_MAX_LINES", 2)),
        subtitle_target_fill=min(1.0, max(0.1, get_float("SUBTITLE_TARGET_FILL", 0.72))),
        subtitle_min_fill=min(1.0, max(0.0, get_float("SUBTITLE_MIN_FILL", 0.28))),
        subtitle_side_margin=max(0, get_int("SUBTITLE_SIDE_MARGIN", 70)),
        subtitle_font=os.getenv("SUBTITLE_FONT", "Arial Rounded MT Bold").strip(),
        subtitle_font_size=max(20, get_int("SUBTITLE_FONT_SIZE", 84)),
        subtitle_outline=max(0, get_int("SUBTITLE_OUTLINE", 6)),
        subtitle_shadow=max(0, get_int("SUBTITLE_SHADOW", 2)),
        subtitle_pop_ms=max(0, get_int("SUBTITLE_POP_MS", 140)),
        channel_name=os.getenv("CHANNEL_NAME", "@RedditBook").strip(),
        title_card_hold_seconds=max(0.0, get_float("TITLE_CARD_HOLD_SECONDS", 0.15)),
    )
