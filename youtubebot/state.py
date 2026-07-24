import json


class UsedContentStore:
    def __init__(self, path):
        self.path = path
        self.values = self.read()

    def read(self):
        if not self.path.exists():
            return set()
        return set(json.loads(self.path.read_text(encoding="utf-8")))

    def contains(self, content_id):
        return content_id in self.values

    def add(self, content_id):
        self.values.add(content_id)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(sorted(self.values), indent=2),
            encoding="utf-8",
        )
