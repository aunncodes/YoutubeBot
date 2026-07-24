import json
import shutil
import subprocess

from youtubebot.rendering.base import Renderer


def require_binary(name):
    if shutil.which(name) is None:
        raise RuntimeError(f"{name} is not installed or not available on PATH")


def audio_duration(path):
    command = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "json",
        str(path.resolve()),
    ]
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    payload = json.loads(result.stdout)
    return float(payload["format"]["duration"])


class FFmpegRenderer(Renderer):
    def __init__(self, settings):
        self.settings = settings
        require_binary("ffmpeg")
        require_binary("ffprobe")

    def render(self, request):
        request.output_path.parent.mkdir(parents=True, exist_ok=True)
        narration_length = audio_duration(request.narration_path)
        total_duration = narration_length + self.settings.outro_hold_seconds
        fade_duration = min(self.settings.video_fade_seconds, total_duration)
        fade_start = max(0.0, total_duration - fade_duration)

        video_filters = (
            f"[0:v]scale={self.settings.video_width}:{self.settings.video_height}:"
            "force_original_aspect_ratio=increase,"
            f"crop={self.settings.video_width}:{self.settings.video_height},"
            "setsar=1,"
            f"fps={self.settings.video_fps},"
            "ass=subtitles.ass,"
            f"fade=t=out:st={fade_start:.3f}:d={fade_duration:.3f}[v]"
        )

        command = [
            "ffmpeg",
            "-y",
            "-stream_loop",
            "-1",
            "-i",
            str(request.background_path.resolve()),
            "-i",
            str(request.narration_path.resolve()),
        ]

        if request.music_path:
            command.extend(
                [
                    "-stream_loop",
                    "-1",
                    "-i",
                    str(request.music_path.resolve()),
                ]
            )
            audio_filters = (
                f"[1:a]apad=pad_dur={self.settings.outro_hold_seconds:.3f},"
                f"atrim=duration={total_duration:.3f}[narration];"
                f"[2:a]volume={self.settings.music_volume:.4f},"
                f"atrim=duration={total_duration:.3f},"
                f"afade=t=out:st={fade_start:.3f}:d={fade_duration:.3f}[music];"
                "[narration][music]"
                "amix=inputs=2:duration=longest:dropout_transition=0:normalize=0,"
                f"atrim=duration={total_duration:.3f}[a]"
            )
        else:
            audio_filters = (
                f"[1:a]apad=pad_dur={self.settings.outro_hold_seconds:.3f},"
                f"atrim=duration={total_duration:.3f},"
                f"afade=t=out:st={fade_start:.3f}:d={fade_duration:.3f}[a]"
            )

        command.extend(
            [
                "-filter_complex",
                f"{video_filters};{audio_filters}",
                "-map",
                "[v]",
                "-map",
                "[a]",
                "-t",
                f"{total_duration:.3f}",
                "-c:v",
                "libx264",
                "-preset",
                self.settings.video_preset,
                "-crf",
                str(self.settings.video_crf),
                "-pix_fmt",
                "yuv420p",
                "-c:a",
                "aac",
                "-b:a",
                "192k",
                "-movflags",
                "+faststart",
                str(request.output_path.resolve()),
            ]
        )

        subprocess.run(command, cwd=request.subtitle_path.parent, check=True)
