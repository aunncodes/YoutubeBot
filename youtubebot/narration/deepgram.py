import io
import json
import re
import wave
from pathlib import Path

import requests

from youtubebot.models import NarrationAsset
from youtubebot.narration.base import Narrator
from youtubebot.narration.timing import WhisperWordTimer


class DeepgramNarrator(Narrator):
    def __init__(self, settings):
        self.settings = settings
        self.word_timer = WhisperWordTimer(settings)

        if not settings.deepgram_api_key:
            raise ValueError("DEEPGRAM_API_KEY is required when TTS_PROVIDER=deepgram")

    def split_text(self, text):
        limit = self.settings.deepgram_chunk_chars
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        chunks = []
        current = ""

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            if len(sentence) > limit:
                if current:
                    chunks.append(current)
                    current = ""
                chunks.extend(self.split_long_sentence(sentence, limit))
                continue

            proposed = sentence if not current else current + " " + sentence
            if len(proposed) <= limit:
                current = proposed
            else:
                chunks.append(current)
                current = sentence

        if current:
            chunks.append(current)

        return chunks

    def split_long_sentence(self, text, limit):
        words = text.split()
        chunks = []
        current = ""

        for word in words:
            proposed = word if not current else current + " " + word
            if len(proposed) <= limit:
                current = proposed
            else:
                if current:
                    chunks.append(current)
                current = word

        if current:
            chunks.append(current)

        return chunks

    def request_audio(self, text):
        response = requests.post(
            "https://api.deepgram.com/v1/speak",
            params={
                "model": self.settings.deepgram_tts_model,
                "encoding": "linear16",
                "container": "wav",
                "sample_rate": "24000",
                "speed": str(self.settings.deepgram_tts_speed),
            },
            headers={
                "Authorization": f"Token {self.settings.deepgram_api_key}",
                "Content-Type": "application/json",
            },
            json={"text": text},
            timeout=180,
        )

        if not response.ok:
            message = response.text.strip()
            raise RuntimeError(
                f"Deepgram TTS failed with status {response.status_code}: {message}"
            )

        return response.content

    def join_waves(self, wav_files, output_path):
        output_params = None
        output_frames = []

        for index, wav_data in enumerate(wav_files):
            with wave.open(io.BytesIO(wav_data), "rb") as source:
                params = (
                    source.getnchannels(),
                    source.getsampwidth(),
                    source.getframerate(),
                )

                if output_params is None:
                    output_params = params
                elif params != output_params:
                    raise RuntimeError("Deepgram returned incompatible audio chunks.")

                if index > 0 and self.settings.deepgram_chunk_pause_ms:
                    channels, sample_width, sample_rate = output_params
                    pause_frames = int(
                        sample_rate * self.settings.deepgram_chunk_pause_ms / 1000
                    )
                    output_frames.append(
                        b"\x00" * pause_frames * channels * sample_width
                    )

                output_frames.append(source.readframes(source.getnframes()))

        if output_params is None:
            raise RuntimeError("Deepgram returned no narration audio.")

        channels, sample_width, sample_rate = output_params
        with wave.open(str(output_path), "wb") as output:
            output.setnchannels(channels)
            output.setsampwidth(sample_width)
            output.setframerate(sample_rate)
            output.writeframes(b"".join(output_frames))

    def synthesize(self, text, output_dir):
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        audio_path = output_dir / "narration.wav"

        chunks = self.split_text(text)
        if not chunks:
            raise ValueError("Narration text is empty.")

        wav_files = []
        for index, chunk in enumerate(chunks, start=1):
            if len(chunks) > 1:
                print(f"Generating Deepgram narration chunk {index} of {len(chunks)}...")
            wav_files.append(self.request_audio(chunk))

        self.join_waves(wav_files, audio_path)
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
