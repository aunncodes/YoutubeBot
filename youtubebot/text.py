import html
import re


WHITESPACE = re.compile(r"\s+")


def clean_reddit_text(value):
    value = html.unescape(value)
    value = value.replace("&amp;#x200B;", " ").replace("&#x200B;", " ")
    value = WHITESPACE.sub(" ", value)
    return value.strip()


def word_count(value):
    return len(value.split())


def build_reddit_narration(title, body, outro_text):
    title = clean_reddit_text(title).rstrip(".?!")
    body = clean_reddit_text(body)
    outro_text = clean_reddit_text(outro_text)
    return f"{title}. {body}... {outro_text}".strip()
