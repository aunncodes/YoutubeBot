import re

from youtubebot.models import SubtitleAsset


class Caption:
    def __init__(self, text, start, end):
        self.text = text
        self.start = start
        self.end = end


def ass_time(seconds):
    centiseconds = max(0, round(seconds * 100))
    hours, remainder = divmod(centiseconds, 360_000)
    minutes, remainder = divmod(remainder, 6_000)
    secs, centis = divmod(remainder, 100)
    return f"{hours}:{minutes:02d}:{secs:02d}.{centis:02d}"


def escape_ass(text):
    return (
        text.replace("\\", r"\\")
        .replace("{", r"\{")
        .replace("}", r"\}")
        .replace("\n", r"\N")
    )


def normalized_word(value):
    return re.sub(r"[^a-z0-9']+", "", value.casefold())


def normalized_tokens(text):
    tokens = []
    for token in text.split():
        token = normalized_word(token)
        if token:
            tokens.append(token)
    return tokens


class AssSubtitleBuilder:
    def __init__(self, settings):
        self.settings = settings

    def build(self, narration, output_dir, title_text):
        title_words, remaining_words = self.split_title_words(narration.words, title_text)
        story_words, outro_words = self.split_outro_words(
            remaining_words,
            self.settings.outro_text,
        )
        captions = self.make_captions(story_words)
        output_dir.mkdir(parents=True, exist_ok=True)
        path = output_dir / "subtitles.ass"
        path.write_text(self.make_document(captions, outro_words), encoding="utf-8")

        title_start = 0.0
        title_end = 0.0
        if title_words:
            title_start = title_words[0].start
            title_end = title_words[-1].end + self.settings.title_card_hold_seconds

        outro_start = 0.0
        outro_end = 0.0
        if outro_words:
            outro_start = outro_words[0].start
            outro_end = max(
                outro_words[-1].end + self.settings.outro_hold_seconds + 0.5,
                outro_start + 1.0,
            )

        return SubtitleAsset(
            path,
            title_start,
            title_end,
            outro_start,
            outro_end,
        )

    def split_title_words(self, words, title_text):
        expected = normalized_tokens(title_text)
        if not expected:
            return [], words

        title_words = []
        consumed_index = 0
        matched = 0

        for index, word in enumerate(words):
            token = normalized_word(word.text)
            if not token:
                continue
            title_words.append(word)
            consumed_index = index + 1
            matched += 1
            if matched >= len(expected):
                break

        return title_words, words[consumed_index:]

    def split_outro_words(self, words, outro_text):
        expected = normalized_tokens(outro_text)
        actual = [normalized_word(word.text) for word in words]

        if not expected or len(actual) < len(expected):
            return words, []

        first_possible = max(0, len(actual) - len(expected) - 4)
        for start in range(len(actual) - len(expected), first_possible - 1, -1):
            if actual[start : start + len(expected)] == expected:
                return words[:start], words[start : start + len(expected)]

        start = len(words) - len(expected)
        return words[:start], words[start:]

    def character_width(self, character):
        if character == " ":
            return 0.32
        if character in "ilI.,'`!|:;":
            return 0.28
        if character in "mwMW@%&QGOD":
            return 0.88
        if character.isupper():
            return 0.70
        if character.isdigit():
            return 0.60
        return 0.56

    def text_width(self, text):
        units = 0.0
        for character in text:
            units += self.character_width(character)
        return units * self.settings.subtitle_font_size

    def layout_widths(self, words):
        max_width = max(
            100,
            self.settings.video_width - self.settings.subtitle_side_margin * 2,
        )
        line_widths = [0.0]
        space_width = self.text_width(" ")

        for word in words:
            word_width = self.text_width(word.text)
            current_width = line_widths[-1]
            extra_width = word_width
            if current_width > 0:
                extra_width += space_width

            if current_width > 0 and current_width + extra_width > max_width:
                line_widths.append(word_width)
            else:
                line_widths[-1] += extra_width

        return line_widths, max_width

    def fill_ratio(self, words):
        line_widths, max_width = self.layout_widths(words)
        capacity = max_width * self.settings.subtitle_max_lines
        return sum(line_widths) / capacity, len(line_widths)

    def can_end_here(self, word):
        value = normalized_word(word.text)
        connectors = {
            "a",
            "an",
            "and",
            "as",
            "at",
            "but",
            "by",
            "for",
            "from",
            "if",
            "in",
            "of",
            "on",
            "or",
            "so",
            "the",
            "to",
            "with",
        }
        return value not in connectors

    def make_captions(self, words):
        captions = []
        chunk = []

        for word in words:
            proposed = chunk + [word]
            duration = proposed[-1].end - proposed[0].start
            fill, line_count = self.fill_ratio(proposed)
            too_many_lines = line_count > self.settings.subtitle_max_lines
            too_long = duration > self.settings.subtitle_max_duration
            too_many_words = len(proposed) > self.settings.subtitle_hard_max_words

            if chunk and (too_many_lines or too_long or too_many_words):
                captions.append(self.caption_from_words(chunk))
                chunk = [word]
            else:
                chunk = proposed

            if not chunk:
                continue

            duration = chunk[-1].end - chunk[0].start
            fill, line_count = self.fill_ratio(chunk)
            strong_punctuation = word.text.endswith((".", "?", "!"))
            soft_punctuation = word.text.endswith((",", ";", ":"))
            reached_target = fill >= self.settings.subtitle_target_fill
            long_enough = duration >= self.settings.subtitle_min_duration
            naturally_finished = self.can_end_here(word)

            if strong_punctuation and len(chunk) >= 2:
                captions.append(self.caption_from_words(chunk))
                chunk = []
            elif soft_punctuation and fill >= self.settings.subtitle_min_fill and long_enough:
                captions.append(self.caption_from_words(chunk))
                chunk = []
            elif reached_target and long_enough and naturally_finished:
                captions.append(self.caption_from_words(chunk))
                chunk = []

        if chunk:
            captions.append(self.caption_from_words(chunk))

        return captions

    def caption_from_words(self, words):
        return Caption(
            " ".join(word.text for word in words),
            words[0].start,
            max(words[-1].end, words[0].start + 0.1),
        )

    def pop_tags(self, start_scale=76):
        if self.settings.subtitle_pop_ms <= 0:
            return ""

        duration = self.settings.subtitle_pop_ms
        return (
            rf"\fscx{start_scale}\fscy{start_scale}"
            rf"\t(0,{duration},\fscx100\fscy100)"
            r"\fad(35,70)"
        )

    def make_document(self, captions, outro_words):
        outro_size = self.settings.subtitle_font_size + 12
        margin = self.settings.subtitle_side_margin
        header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {self.settings.video_width}
PlayResY: {self.settings.video_height}
ScaledBorderAndShadow: yes
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Main,{self.settings.subtitle_font},{self.settings.subtitle_font_size},&H00FFFFFF,&H0000FFFF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,{self.settings.subtitle_outline},{self.settings.subtitle_shadow},5,{margin},{margin},100,1
Style: Outro,{self.settings.subtitle_font},{outro_size},&H00FFFFFF,&H0000FFFF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,{self.settings.subtitle_outline},{self.settings.subtitle_shadow},5,{margin},{margin},100,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
        pop = self.pop_tags()
        events = []

        for caption in captions:
            events.append(
                "Dialogue: 0,"
                f"{ass_time(caption.start)},{ass_time(caption.end)},"
                f"Main,,0,0,0,,{{{pop}}}{escape_ass(caption.text)}"
            )

        if outro_words:
            start = outro_words[0].start
            end = max(
                outro_words[-1].end + self.settings.outro_hold_seconds + 0.5,
                start + 1.0,
            )
            center_x = self.settings.video_width // 2
            center_y = self.settings.video_height // 2 - 90
            outro_parts = re.split(r"(?<=[?!])\s+", self.settings.outro_text.upper())
            outro_text = r"\N".join(escape_ass(part) for part in outro_parts)
            outro_pop = self.pop_tags(68)

            events.append(
                "Dialogue: 1,"
                f"{ass_time(start)},{ass_time(end)},"
                "Outro,,0,0,0,,"
                f"{{\\pos({center_x},{center_y}){outro_pop}}}{outro_text}"
            )

        return header + "\n".join(events) + "\n"
