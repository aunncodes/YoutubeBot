import json


from youtubebot.models import NarrationAsset, TimedWord
from youtubebot.narration.base import Narrator


TICKS_PER_SECOND = 10_000_000


class EdgeTTSNarrator(Narrator):
    def __init__(self, settings):
        self.settings = settings

    def synthesize(self, text, output_dir):
        import edge_tts

        output_dir.mkdir(parents=True, exist_ok=True)
        audio_path = output_dir / "narration.mp3"
        timing_path = output_dir / "narration-timings.json"

        communicator = edge_tts.Communicate(
            text,
            voice=self.settings.edge_tts_voice,
            rate=self.settings.edge_tts_rate,
            volume=self.settings.edge_tts_volume,
            pitch=self.settings.edge_tts_pitch,
            boundary="WordBoundary",
        )

        words = []
        with audio_path.open("wb") as audio_file:
            for message in communicator.stream_sync():
                if message["type"] == "audio":
                    audio_file.write(message["data"])
                elif message["type"] == "WordBoundary":
                    word = self.word_from_message(message)
                    if word.text:
                        words.append(word)

        timing_path.write_text(
            json.dumps(
                [
                    {"text": word.text, "start": word.start, "end": word.end}
                    for word in words
                ],
                indent=2,
            ),
            encoding="utf-8",
        )

        return NarrationAsset(audio_path, text, words)

    def word_from_message(self, message):
        offset = int(message["offset"])
        duration = int(message["duration"])
        return TimedWord(
            str(message["text"]).strip(),
            offset / TICKS_PER_SECOND,
            (offset + duration) / TICKS_PER_SECOND,
        )
