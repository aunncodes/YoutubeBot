from pathlib import Path

from youtubebot.models import TimedWord


class WhisperWordTimer:
    def __init__(self, settings):
        self.settings = settings
        self.model = None

    def load(self):
        if self.model is not None:
            return

        import whisper

        self.model = whisper.load_model(
            self.settings.whisper_model,
            device=self.settings.whisper_device,
        )

    def get_words(self, audio_path):
        self.load()

        result = self.model.transcribe(
            str(Path(audio_path).resolve()),
            language="en",
            word_timestamps=True,
            fp16=False,
            condition_on_previous_text=False,
            verbose=False,
        )

        words = []
        for segment in result.get("segments", []):
            for word in segment.get("words", []):
                text = word.get("word", "").strip()
                if not text:
                    continue

                start = float(word.get("start", 0.0))
                end = float(word.get("end", start + 0.1))

                if end <= start:
                    end = start + 0.1

                words.append(TimedWord(text, start, end))

        if not words:
            raise RuntimeError("Whisper did not produce word timings for the narration audio.")

        return words
