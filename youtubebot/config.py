import os
from pathlib import Path


def get_int(name, default):
    return int(os.getenv(name, default))


def get_float(name, default):
    return float(os.getenv(name, default))


class Settings:
    def __init__(
        self,
        project_root,
        reddit_client_id,
        reddit_client_secret,
        reddit_user_agent,
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
        video_width,
        video_height,
        video_fps,
        video_crf,
        video_preset,
        video_fade_seconds,
        music_volume,
        outro_text,
        subscribe_text,
        outro_hold_seconds,
        subtitle_max_words,
        subtitle_max_duration,
        subtitle_font,
        subtitle_font_size,
        subtitle_pop_ms,
        channel_name,
        title_card_hold_seconds,
        title_card_top,
    ):
        self.project_root = project_root
        self.reddit_client_id = reddit_client_id
        self.reddit_client_secret = reddit_client_secret
        self.reddit_user_agent = reddit_user_agent
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
        self.video_width = video_width
        self.video_height = video_height
        self.video_fps = video_fps
        self.video_crf = video_crf
        self.video_preset = video_preset
        self.video_fade_seconds = video_fade_seconds
        self.music_volume = music_volume
        self.outro_text = outro_text
        self.subscribe_text = subscribe_text
        self.outro_hold_seconds = outro_hold_seconds
        self.subtitle_max_words = subtitle_max_words
        self.subtitle_max_duration = subtitle_max_duration
        self.subtitle_font = subtitle_font
        self.subtitle_font_size = subtitle_font_size
        self.subtitle_pop_ms = subtitle_pop_ms
        self.channel_name = channel_name
        self.title_card_hold_seconds = title_card_hold_seconds
        self.title_card_top = title_card_top
        self.reddit_background_dir = project_root / "assets" / "backgrounds" / "reddit"
        self.music_dir = project_root / "assets" / "music"
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

    chatterbox_voice_path = normalize_path(
        os.getenv("CHATTERBOX_VOICE_PATH", "").strip(),
        root,
    )

    return Settings(
        project_root=root,
        reddit_client_id=os.getenv("REDDIT_CLIENT_ID").strip(),
        reddit_client_secret=os.getenv("REDDIT_CLIENT_SECRET").strip(),
        reddit_user_agent=os.getenv("REDDIT_USER_AGENT").strip(),
        chatterbox_device=choose_chatterbox_device(
            os.getenv("CHATTERBOX_DEVICE", "").strip()
        ),
        chatterbox_voice_path=chatterbox_voice_path,
        chatterbox_exaggeration=get_float("CHATTERBOX_EXAGGERATION", 0.65),
        chatterbox_cfg_weight=get_float("CHATTERBOX_CFG_WEIGHT", 0.35),
        whisper_model=os.getenv("WHISPER_MODEL", "tiny.en").strip(),
        whisper_device=os.getenv("WHISPER_DEVICE", "cpu").strip(),
        reddit_subreddits=subreddits,
        reddit_listing_limit=get_int("REDDIT_LISTING_LIMIT", 60),
        reddit_selection_pool=max(1, get_int("REDDIT_SELECTION_POOL", 12)),
        reddit_max_age_hours=get_float("REDDIT_MAX_AGE_HOURS", 48),
        reddit_min_score=get_int("REDDIT_MIN_SCORE", 500),
        reddit_min_comments=get_int("REDDIT_MIN_COMMENTS", 40),
        reddit_min_upvote_ratio=get_float("REDDIT_MIN_UPVOTE_RATIO", 0.85),
        reddit_min_words=get_int("REDDIT_MIN_WORDS", 120),
        reddit_max_words=get_int("REDDIT_MAX_WORDS", 450),
        video_width=get_int("VIDEO_WIDTH", 1080),
        video_height=get_int("VIDEO_HEIGHT", 1920),
        video_fps=get_int("VIDEO_FPS", 30),
        video_crf=get_int("VIDEO_CRF", 20),
        video_preset=os.getenv("VIDEO_PRESET", "medium").strip(),
        video_fade_seconds=max(0.1, get_float("VIDEO_FADE_SECONDS", 1.0)),
        music_volume=max(0.0, get_float("MUSIC_VOLUME", 0.055)),
        outro_text=os.getenv(
            "OUTRO_TEXT",
            "So what do you think? Comment down below!",
        ).strip(),
        subscribe_text=os.getenv("SUBSCRIBE_TEXT", "SUBSCRIBE").strip(),
        outro_hold_seconds=max(0.0, get_float("OUTRO_HOLD_SECONDS", 1.4)),
        subtitle_max_words=get_int("SUBTITLE_MAX_WORDS", 5),
        subtitle_max_duration=get_float("SUBTITLE_MAX_DURATION", 2.2),
        subtitle_font=os.getenv("SUBTITLE_FONT", "Arial").strip(),
        subtitle_font_size=get_int("SUBTITLE_FONT_SIZE", 72),
        subtitle_pop_ms=max(0, get_int("SUBTITLE_POP_MS", 140)),
        channel_name=os.getenv("CHANNEL_NAME", "@RedditBook").strip(),
        title_card_hold_seconds=max(0.0, get_float("TITLE_CARD_HOLD_SECONDS", 0.15)),
        title_card_top=get_int("TITLE_CARD_TOP", 30),
    )
