TITLE_LIMIT = 100
DESCRIPTION_LIMIT = 5000
VIDEO_TAG_LIMIT = 500
MAX_TOTAL_HASHTAGS = 55


CORE_TITLE_HASHTAGS = [
    "#shorts",
    "#reddit",
    "#redditstories",
    "#redditstory",
    "#redditstorytime",
]


GENERAL_HASHTAGS = [
    "#redditshorts",
    "#youtubeshorts",
    "#shortsvideo",
    "#shortsfeed",
    "#storytime",
    "#story",
    "#stories",
    "#viralstories",
    "#viralstory",
    "#redditvideo",
    "#redditvideos",
    "#redditpost",
    "#redditposts",
    "#redditcommunity",
    "#redditreading",
    "#redditreadings",
    "#redditnarration",
    "#narratedstories",
    "#storytelling",
    "#shortstory",
    "#internetstories",
    "#socialmediastories",
    "#onlinestories",
    "#redditthread",
    "#redditthreads",
    "#threadstory",
    "#commentary",
    "#narration",
    "#voiceover",
    "#dramastory",
    "#reallifestories",
    "#interestingstories",
    "#mustwatch",
    "#trending",
    "#viral",
    "#minecraftparkour",
    "#minecraft",
    "#minecraftshorts",
    "#parkour",
    "#backgroundgameplay",
    "#gamingbackground",
]


SUBREDDIT_HASHTAGS = {
    "aitah": [
        "#aita",
        "#aitah",
        "#amitheasshole",
        "#redditaita",
        "#aitastories",
        "#aitareddit",
        "#moraldilemma",
        "#whoswrong",
        "#redditadvice",
        "#lifeadvice",
        "#relationshipdrama",
        "#familydrama",
        "#drama",
        "#confession",
        "#confessions",
    ],
    "amitheasshole": [
        "#aita",
        "#aitah",
        "#amitheasshole",
        "#redditaita",
        "#aitastories",
        "#aitareddit",
        "#moraldilemma",
        "#whoswrong",
        "#redditadvice",
        "#lifeadvice",
        "#relationshipdrama",
        "#familydrama",
        "#drama",
        "#confession",
        "#confessions",
    ],
    "trueoffmychest": [
        "#trueoffmychest",
        "#offmychest",
        "#confession",
        "#confessions",
        "#personalstory",
        "#reallifestory",
        "#emotionalstory",
        "#lifeadvice",
        "#redditconfessions",
    ],
    "pettyrevenge": [
        "#pettyrevenge",
        "#revenge",
        "#revengestory",
        "#karma",
        "#instantkarma",
        "#justice",
        "#satisfyingstory",
        "#redditrevenge",
    ],
    "maliciouscompliance": [
        "#maliciouscompliance",
        "#workstories",
        "#workplace",
        "#workdrama",
        "#office",
        "#boss",
        "#coworkers",
        "#karma",
        "#redditworkstories",
    ],
    "askreddit": [
        "#askreddit",
        "#redditquestions",
        "#redditanswers",
        "#questions",
        "#answers",
        "#discussion",
    ],
    "relationship_advice": [
        "#relationshipadvice",
        "#relationships",
        "#datingadvice",
        "#relationshipdrama",
        "#dating",
        "#loveadvice",
    ],
}


KEYWORD_HASHTAGS = [
    (("boyfriend", "girlfriend", "dating", "relationship", "fiance", "fiancée"), [
        "#relationship",
        "#relationships",
        "#relationshipadvice",
        "#dating",
        "#datingstory",
    ]),
    (("husband", "wife", "marriage", "married", "wedding"), [
        "#marriage",
        "#marriagestory",
        "#weddingdrama",
        "#relationshipdrama",
    ]),
    (("mother", "father", "mom", "dad", "sister", "brother", "family", "parent"), [
        "#family",
        "#familydrama",
        "#familystory",
        "#parents",
        "#siblings",
    ]),
    (("mother-in-law", "father-in-law", "mil", "fil", "sil", "bil", "in-law"), [
        "#inlaws",
        "#motherinlaw",
        "#familydrama",
    ]),
    (("boss", "coworker", "coworker", "job", "work", "office", "manager"), [
        "#work",
        "#workplace",
        "#workstories",
        "#workdrama",
        "#coworkers",
        "#boss",
    ]),
    (("teacher", "student", "school", "college", "university", "class"), [
        "#school",
        "#schoolstory",
        "#college",
        "#studentlife",
        "#teacherstory",
    ]),
    (("roommate", "roommates"), [
        "#roommate",
        "#roommatedrama",
        "#roommatestory",
    ]),
    (("neighbor", "neighbour"), [
        "#neighbors",
        "#neighbordrama",
        "#neighborstory",
    ]),
    (("cheat", "cheated", "cheating", "affair", "betray"), [
        "#cheating",
        "#betrayal",
        "#relationshipdrama",
    ]),
    (("revenge", "karma", "payback"), [
        "#revenge",
        "#karma",
        "#payback",
        "#revengestory",
    ]),
    (("money", "rent", "debt", "inheritance", "loan", "paid"), [
        "#money",
        "#financialdrama",
        "#moneystory",
    ]),
]


GENERAL_VIDEO_TAGS = [
    "reddit stories",
    "reddit story",
    "reddit",
    "reddit storytime",
    "reddit shorts",
    "reddit video",
    "reddit videos",
    "reddit post",
    "reddit posts",
    "reddit thread",
    "reddit threads",
    "reddit narration",
    "reddit reading",
    "storytime",
    "story time",
    "short stories",
    "viral stories",
    "internet stories",
    "social media stories",
    "online stories",
    "real life stories",
    "dramatic stories",
    "narrated stories",
    "storytelling",
    "youtube shorts",
    "shorts",
    "shorts video",
    "shorts feed",
    "viral shorts",
    "minecraft parkour",
    "minecraft shorts",
    "minecraft gameplay",
    "background gameplay",
    "reddit minecraft parkour",
    "voiceover",
    "commentary",
]


def unique_values(values):
    result = []
    seen = set()

    for value in values:
        key = value.casefold()
        if value and key not in seen:
            result.append(value)
            seen.add(key)

    return result


def subreddit_key(item):
    value = str(item.metadata.get("subreddit", "reddit")).strip()
    return value.casefold().replace("r/", "")


def keyword_hashtags(item):
    text = f"{item.title} {item.body}".casefold()
    result = []

    for keywords, hashtags in KEYWORD_HASHTAGS:
        if any(keyword in text for keyword in keywords):
            result.extend(hashtags)

    return result


def make_hashtag_pool(item):
    subreddit = subreddit_key(item)
    subreddit_tag = "#" + "".join(character for character in subreddit if character.isalnum())

    return unique_values(
        CORE_TITLE_HASHTAGS
        + SUBREDDIT_HASHTAGS.get(subreddit, [])
        + keyword_hashtags(item)
        + [subreddit_tag]
        + GENERAL_HASHTAGS
    )


def truncate_text(text, limit):
    text = text.strip()

    if len(text) <= limit:
        return text

    if limit <= 1:
        return text[:limit]

    return text[: limit - 1].rstrip() + "…"


def make_upload_title(item):
    hashtags = make_hashtag_pool(item)
    required = CORE_TITLE_HASHTAGS
    required_text = " ".join(required)
    title_limit = TITLE_LIMIT - len(required_text) - 1
    title_text = truncate_text(item.title, max(1, title_limit))
    title = f"{title_text} {required_text}".strip()

    for hashtag in hashtags:
        if hashtag in required:
            continue

        candidate = f"{title} {hashtag}"
        if len(candidate) > TITLE_LIMIT:
            continue
        title = candidate

    return title


def hashtags_in_title(title):
    return [word for word in title.split() if word.startswith("#")]


def make_description(item, title):
    title_hashtags = hashtags_in_title(title)
    all_hashtags = make_hashtag_pool(item)
    remaining_limit = max(0, MAX_TOTAL_HASHTAGS - len(title_hashtags))
    description_hashtags = []

    for hashtag in all_hashtags:
        if hashtag in title_hashtags:
            continue
        description_hashtags.append(hashtag)
        if len(description_hashtags) >= remaining_limit:
            break

    main_text = (
        f"{item.title}\n\n"
        "What do you think? Comment below and subscribe for more Reddit stories.\n\n"
        f"Original post: {item.url}\n\n"
    )
    hashtag_text = " ".join(description_hashtags)
    description = main_text + hashtag_text

    return description[:DESCRIPTION_LIMIT].rstrip()


def video_tag_cost(tags):
    total = 0

    for index, tag in enumerate(tags):
        if index:
            total += 1
        total += len(tag)
        if " " in tag:
            total += 2

    return total


def make_video_tag_pool(item):
    subreddit = str(item.metadata.get("subreddit", "reddit")).strip()
    hashtag_words = []

    for hashtag in make_hashtag_pool(item):
        hashtag_words.append(hashtag.lstrip("#"))

    return unique_values(
        [subreddit, f"r {subreddit}", f"reddit {subreddit}"]
        + hashtag_words
        + GENERAL_VIDEO_TAGS
    )


def make_tags(item):
    tags = []

    for tag in make_video_tag_pool(item):
        candidate = tags + [tag]
        if video_tag_cost(candidate) > VIDEO_TAG_LIMIT:
            continue
        tags.append(tag)

    return tags


def get_tts_voice(settings):
    if settings.tts_provider == "gemini":
        return settings.gemini_tts_voice

    if settings.tts_provider == "deepgram":
        return settings.deepgram_tts_model

    if settings.chatterbox_voice_path:
        return str(settings.chatterbox_voice_path)

    return "chatterbox-default"


def make_upload_metadata(item, narration_text, background, music, settings):
    title = make_upload_title(item)

    return {
        "title": title,
        "description": make_description(item, title),
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
