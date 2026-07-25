import base64
import json
import wave
from pathlib import Path

from google import genai

from youtubebot.models import NarrationAsset
from youtubebot.narration.base import Narrator
from youtubebot.narration.timing import WhisperWordTimer


class GeminiNarrator(Narrator):
    def __init__(self, settings):
        self.settings = settings
        self.word_timer = WhisperWordTimer(settings)

        if not settings.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is required when TTS_PROVIDER=gemini")

        self.client = genai.Client(api_key=settings.gemini_api_key)

    def make_prompt(self, text):
        return (
            self.settings.gemini_tts_style
            + "\n\nTRANSCRIPT:\n"
            + text
        )

    def save_wave(self, path, pcm):
        with wave.open(str(path), "wb") as file:
            file.setnchannels(1)
            file.setsampwidth(2)
            file.setframerate(24000)
            file.writeframes(pcm)

    def synthesize(self, text, output_dir):
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        audio_path = output_dir / "narration.wav"

        interaction = self.client.interactions.create(
            model=self.settings.gemini_tts_model,
            input=self.make_prompt(text),
            response_format={"type": "audio"},
            generation_config={
                "speech_config": [
                    {"voice": self.settings.gemini_tts_voice}
                ]
            },
        )

        if not interaction.output_audio or not interaction.output_audio.data:
            raise RuntimeError("Gemini returned no narration audio.")

        audio_data = interaction.output_audio.data
        if isinstance(audio_data, str):
            pcm = base64.b64decode(audio_data)
        else:
            pcm = bytes(audio_data)

        self.save_wave(audio_path, pcm)
        words = self.word_timer.get_words(audio_path)

        timing_payload = []
        for word in words:
            timing_payload.append(
                {
                    "text": word.text,
                    "start": word.start,
                    "end": word.end,
                }
            )

        timing_path = output_dir / "narration-timings.json"
        timing_path.write_text(json.dumps(timing_payload, indent=2), encoding="utf-8")

        return NarrationAsset(audio_path, text, words)
