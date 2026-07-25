import json
from datetime import datetime, timezone
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"


class YouTubeUploader:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.client_secret_path = self.project_root / "client_secret.json"
        self.token_path = self.project_root / "youtube_token.json"
        self.youtube = self.connect()

    def connect(self):
        credentials = None

        if self.token_path.exists():
            credentials = Credentials.from_authorized_user_file(
                self.token_path,
                [YOUTUBE_UPLOAD_SCOPE],
            )

        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())

        if not credentials or not credentials.valid:
            if not self.client_secret_path.exists():
                raise FileNotFoundError(
                    f"Missing OAuth file: {self.client_secret_path}"
                )

            flow = InstalledAppFlow.from_client_secrets_file(
                self.client_secret_path,
                [YOUTUBE_UPLOAD_SCOPE],
            )
            credentials = flow.run_local_server(
                port=0,
                access_type="offline",
                prompt="consent",
            )

        self.token_path.write_text(credentials.to_json(), encoding="utf-8")

        return build(
            "youtube",
            "v3",
            credentials=credentials,
            cache_discovery=False,
        )

    def upload(self, video_path, metadata_path):
        video_path = Path(video_path)
        metadata_path = Path(metadata_path)
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))

        if metadata.get("upload_status") == "uploaded":
            return metadata

        metadata["upload_status"] = "uploading"
        metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

        body = {
            "snippet": {
                "title": metadata["title"],
                "description": metadata["description"],
                "tags": metadata.get("tags", []),
                "categoryId": metadata.get("category_id", "24"),
            },
            "status": {
                "privacyStatus": metadata.get("privacy_status", "private"),
                "selfDeclaredMadeForKids": metadata.get("made_for_kids", False),
                "containsSyntheticMedia": metadata.get(
                    "contains_synthetic_media",
                    True,
                ),
            },
        }

        media = MediaFileUpload(
            str(video_path),
            mimetype="video/mp4",
            chunksize=-1,
            resumable=True,
        )
        request = self.youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media,
            notifySubscribers=False,
        )

        response = None

        try:
            while response is None:
                status, response = request.next_chunk(num_retries=3)

                if status:
                    percent = int(status.progress() * 100)
                    print(f"Upload progress: {percent}%")
        except Exception as error:
            metadata["upload_status"] = "failed"
            metadata["upload_error"] = str(error)
            metadata_path.write_text(
                json.dumps(metadata, indent=2),
                encoding="utf-8",
            )
            raise

        video_id = response["id"]
        metadata["upload_status"] = "uploaded"
        metadata.pop("upload_error", None)
        metadata["youtube_video_id"] = video_id
        metadata["youtube_url"] = f"https://www.youtube.com/watch?v={video_id}"
        metadata["uploaded_at"] = datetime.now(timezone.utc).isoformat()
        metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

        return metadata
