import re

from youtubebot.text import clean_reddit_text


TITLE_LIMIT = 100


def make_hashtag(value):
    value = re.sub(r"[^a-zA-Z0-9]", "", value)
    return f"#{value.lower()}" if value else ""


def shorten(value, limit):
    value = clean_reddit_text(value)
    if len(value) <= limit:
        return value

    shortened = value[: max(0, limit - 3)].rstrip()
    return shortened + "..."


def make_upload_title(item):
    subreddit = item.metadata.get("subreddit", "reddit")
    hashtags = [
        make_hashtag(subreddit),
        "#redditstories",
        "#reddit",
        "#shorts",
    ]
    hashtags = [tag for tag in hashtags if tag]
    suffix = " " + " ".join(hashtags)
    story_title = shorten(item.title, TITLE_LIMIT - len(suffix))
    return story_title + suffix


def make_description(item):
    subreddit = item.metadata.get("subreddit", "reddit")
    specific_tag = make_hashtag(subreddit)
    hashtags = [
        specific_tag,
        "#redditstories",
        "#reddit",
        "#storytime",
        "#redditstory",
        "#shorts",
        "#viral",
        "#minecraftparkour",
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


def make_upload_metadata(item, narration_text, background, music, settings):
    return {
        "title": make_upload_title(item),
        "description": make_description(item),
        "tags": make_tags(item),
        "category_id": "24",
        "privacy_status": "private",
        "made_for_kids": False,
        "source_url": item.url,
        "source_id": item.source_id,
        "source_author": item.author,
        "source_metadata": item.metadata,
        "narration_text": narration_text,
        "background": str(background),
        "music": str(music) if music else None,
        "tts_voice": settings.edge_tts_voice,
    }
