import re


REDDIT_REPLACEMENTS = [
    (r"\bWIBTAH\b", "would I be the asshole", True),
    (r"\bWIBTA\b", "would I be the asshole", True),
    (r"\bAITAH\b", "am I the asshole", True),
    (r"\bAITA\b", "am I the asshole", True),
    (r"\bNTA\b", "not the asshole", False),
    (r"\bYTA\b", "you're the asshole", False),
    (r"\bESH\b", "everyone sucks here", False),
    (r"\bNAH\b", "no assholes here", False),
    (r"\bINFO\b", "more information needed", False),
    (r"\bOOP\b", "original original poster", False),
    (r"\bOP\b", "original poster", False),
    (r"\bMIL\b", "mother-in-law", False),
    (r"\bFIL\b", "father-in-law", False),
    (r"\bSIL\b", "sister-in-law", False),
    (r"\bBIL\b", "brother-in-law", False),
    (r"\bBF\b", "boyfriend", False),
    (r"\bGF\b", "girlfriend", False),
    (r"\bSO\b", "significant other", False),
    (r"\bFWB\b", "friend with benefits", False),
    (r"\bSAHM\b", "stay-at-home mom", False),
    (r"\bSAHD\b", "stay-at-home dad", False),
    (r"\bNC\b", "no contact", False),
    (r"\bLC\b", "low contact", False),
    (r"\bTL\s*;?\s*DR\b", "too long, didn't read", True),
]


def expand_reddit_acronyms(text):
    for pattern, replacement, ignore_case in REDDIT_REPLACEMENTS:
        flags = re.IGNORECASE if ignore_case else 0
        text = re.sub(pattern, replacement, text, flags=flags)

    return text


def estimate_narration_seconds(text, words_per_minute, extra_seconds=0.0):
    words = re.findall(r"\b[\w'-]+\b", text)
    spoken_seconds = len(words) / max(1.0, words_per_minute) * 60.0
    return spoken_seconds + max(0.0, extra_seconds)
