class ContentItem:
    def __init__(self, source, source_id, title, body, author, url, metadata):
        self.source = source
        self.source_id = source_id
        self.title = title
        self.body = body
        self.author = author
        self.url = url
        self.metadata = metadata


class TimedWord:
    def __init__(self, text, start, end):
        self.text = text
        self.start = start
        self.end = end


class NarrationAsset:
    def __init__(self, audio_path, text, words):
        self.audio_path = audio_path
        self.text = text
        self.words = words


class SubtitleAsset:
    def __init__(self, path):
        self.path = path


class RenderRequest:
    def __init__(
        self,
        background_path,
        narration_path,
        subtitle_path,
        output_path,
        music_path=None,
    ):
        self.background_path = background_path
        self.narration_path = narration_path
        self.subtitle_path = subtitle_path
        self.output_path = output_path
        self.music_path = music_path


class VideoResult:
    def __init__(self, output_path, source_url, title, metadata_path):
        self.output_path = output_path
        self.source_url = source_url
        self.title = title
        self.metadata_path = metadata_path
