def trim_title_to_limit(text, hashtags, limit=100):
    suffix = " " + " ".join(hashtags)
    max_text = max(1, limit - len(suffix))
    text = text.strip()

    if len(text) > max_text:
        text = text[: max_text - 1].rstrip()
        text += "…"

    return (text + suffix).strip()


def make_upload_title(item):
    subreddit = item.metadata.get("subreddit", "reddit")
    title_prefix = item.title.strip()
    hashtags = ["#redditstories", "#reddit", "#shorts"]
    return trim_title_to_limit(f"{title_prefix} | r/{subreddit}", hashtags)


def make_description(item):
    hashtags = [
        "#redditstories",
        "#reddit",
        "#shorts",
        "#storytime",
        "#aita",
        "#aitah",
        "#askreddit",
    ]
    hashtags = list(dict.fromkeys(tag for tag in hashtags if tag))

    return (
        "What do you think? Comment below and subscribe for more Reddit stories.\n\n"
        f"Original post: {item.url}\n\n"
        + " ".join(hashtags)
    )


def make_tags(item):
    subreddit = item.metadata.get("subreddit", "reddit")
    return [
        "reddit stories",
        "reddit story",
        "reddit",
        "storytime",
        "reddit shorts",
        "youtube shorts",
        "shorts",
        "viral stories",
        "minecraft parkour",
        "aita",
        "aitah",
        subreddit,
    ]


def get_tts_voice(settings):
    if settings.tts_provider == "gemini":
        return settings.gemini_tts_voice

    if settings.tts_provider == "deepgram":
        return settings.deepgram_tts_model

    if settings.chatterbox_voice_path:
        return str(settings.chatterbox_voice_path)

    return "chatterbox-default"


def make_upload_metadata(item, narration_text, background, music, settings):
    return {
        "title": make_upload_title(item),
        "description": make_description(item),
        "tags": make_tags(item),
        "category_id": "24",
        "privacy_status": "private",
        "made_for_kids": False,
        "contains_synthetic_media": True,
        "upload_status": "pending",
        "youtube_video_id": None,
        "youtube_url": None,
        "uploaded_at": None,
        "source_url": item.url,
        "source_id": item.source_id,
        "source_author": item.author,
        "source_metadata": item.metadata,
        "narration_text": narration_text,
        "background": str(background),
        "music": str(music) if music else None,
        "tts_provider": settings.tts_provider,
        "tts_voice": get_tts_voice(settings),
    }
