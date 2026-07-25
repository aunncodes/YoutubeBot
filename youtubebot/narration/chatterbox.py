import json
from pathlib import Path

import soundfile as sf

from youtubebot.models import NarrationAsset, TimedWord
from youtubebot.narration.base import Narrator


class ChatterboxNarrator(Narrator):
    def __init__(self, settings):
        self.settings = settings
        self.tts_model = None
        self.whisper_model = None
        self.sample_rate = None

    def load_tts(self):
        if self.tts_model is not None:
            return

        import torch
        from chatterbox.tts import ChatterboxTTS

        device = self.settings.chatterbox_device
        map_location = torch.device(device)
        original_torch_load = torch.load

        def patched_torch_load(*args, **kwargs):
            if "map_location" not in kwargs:
                kwargs["map_location"] = map_location
            return original_torch_load(*args, **kwargs)

        torch.load = patched_torch_load

        try:
            self.tts_model = ChatterboxTTS.from_pretrained(device=device)
            self.sample_rate = self.tts_model.sr
        finally:
            torch.load = original_torch_load

    def load_whisper(self):
        if self.whisper_model is not None:
            return

        import whisper

        self.whisper_model = whisper.load_model(
            self.settings.whisper_model,
            device=self.settings.whisper_device,
        )

    def synthesize(self, text, output_dir):
        self.load_tts()
        self.load_whisper()

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        kwargs = {
            "exaggeration": self.settings.chatterbox_exaggeration,
            "cfg_weight": self.settings.chatterbox_cfg_weight,
        }

        voice_path = self.settings.chatterbox_voice_path
        if voice_path and Path(voice_path).exists():
            kwargs["audio_prompt_path"] = str(Path(voice_path).resolve())

        audio = self.tts_model.generate(text, **kwargs)
        audio_data = audio.squeeze().detach().cpu().numpy()
        audio_path = output_dir / "narration.wav"
        sf.write(audio_path, audio_data, self.sample_rate)

        words = self.transcribe_words(audio_path)
        timing_path = output_dir / "narration-timings.json"
        timing_payload = []
        for word in words:
            timing_payload.append(
                {
                    "text": word.text,
                    "start": word.start,
                    "end": word.end,
                }
            )
        timing_path.write_text(json.dumps(timing_payload, indent=2), encoding="utf-8")

        return NarrationAsset(audio_path, text, words)

    def transcribe_words(self, audio_path):
        result = self.whisper_model.transcribe(
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
