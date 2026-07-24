import math
import random
import time


from youtubebot.models import ContentItem
from youtubebot.sources.base import ContentSource
from youtubebot.text import clean_reddit_text, word_count


class RedditStorySource(ContentSource):
    def __init__(self, settings, used_store):
        import praw

        self.settings = settings
        self.used_store = used_store
        self.reddit = praw.Reddit(
            client_id=settings.reddit_client_id,
            client_secret=settings.reddit_client_secret,
            user_agent=settings.reddit_user_agent,
            check_for_async=False,
        )
        self.reddit.read_only = True

    def fetch(self):
        candidates = list(self.discover_candidates())
        if not candidates:
            raise RuntimeError(
                "No eligible Reddit stories were found. Lower the filters or add more subreddits."
            )

        candidates.sort(key=self.momentum_score, reverse=True)
        pool = candidates[: self.settings.reddit_selection_pool]
        submission = self.weighted_choice(pool)
        return self.to_item(submission)

    def discover_candidates(self):
        combined_name = "+".join(self.settings.reddit_subreddits)
        subreddit = self.reddit.subreddit(combined_name)
        seen = set()

        listings = [
            subreddit.top(time_filter="day", limit=self.settings.reddit_listing_limit),
            subreddit.hot(limit=self.settings.reddit_listing_limit),
            subreddit.rising(limit=self.settings.reddit_listing_limit),
        ]

        for listing in listings:
            for submission in listing:
                if submission.id in seen:
                    continue
                seen.add(submission.id)
                if self.eligible(submission):
                    yield submission

    def eligible(self, submission):
        body = clean_reddit_text(submission.selftext or "")
        words = word_count(body)
        age_hours = max(0.0, (time.time() - submission.created_utc) / 3600)

        if self.used_store.contains(submission.id):
            return False
        if submission.over_18 or submission.stickied:
            return False
        if body in {"", "[removed]", "[deleted]"}:
            return False
        if words < self.settings.reddit_min_words:
            return False
        if words > self.settings.reddit_max_words:
            return False
        if age_hours > self.settings.reddit_max_age_hours:
            return False
        if submission.score < self.settings.reddit_min_score:
            return False
        if submission.num_comments < self.settings.reddit_min_comments:
            return False
        if submission.upvote_ratio < self.settings.reddit_min_upvote_ratio:
            return False
        return True

    def weighted_choice(self, candidates):
        scores = [self.momentum_score(candidate) for candidate in candidates]
        best_score = max(scores)
        weights = [math.exp((score - best_score) / 1.75) for score in scores]
        return random.choices(candidates, weights=weights, k=1)[0]

    def momentum_score(self, submission):
        age_hours = max(0.0, (time.time() - submission.created_utc) / 3600)
        freshness = max(
            0.0,
            1.0 - age_hours / max(1.0, self.settings.reddit_max_age_hours),
        )
        return (
            math.log1p(max(0, submission.score))
            + 1.25 * math.log1p(max(0, submission.num_comments))
            + 2.0 * float(submission.upvote_ratio)
            + 3.0 * freshness
        )

    def to_item(self, submission):
        author = str(submission.author) if submission.author else None
        return ContentItem(
            "reddit",
            submission.id,
            clean_reddit_text(submission.title),
            clean_reddit_text(submission.selftext),
            author,
            f"https://www.reddit.com{submission.permalink}",
            {
                "subreddit": str(submission.subreddit),
                "score": int(submission.score),
                "comments": int(submission.num_comments),
                "upvote_ratio": float(submission.upvote_ratio),
                "created_utc": float(submission.created_utc),
            },
        )
