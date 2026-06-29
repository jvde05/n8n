"""Native YouTube yukleyici (Data API v3, resumable upload).

n8n'e bagimli degildir. Kimlikler (kanal bazli olabilir):
  YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN
"""
import json
import os

from ...errors import PublishError
from ...interfaces import Publisher, PublishResult
from ...logging_utils import get_logger
from ...platforms import build_metadata
from .google_oauth import access_token

log = get_logger("publish.youtube")
UPLOAD_URL = ("https://www.googleapis.com/upload/youtube/v3/videos"
              "?uploadType=resumable&part=snippet,status")


class YouTubeAPIPublisher(Publisher):
    platform = "youtube"

    def publish(self, video_path: str, job: dict, credentials: dict) -> PublishResult:
        import requests  # lazy

        channel = (credentials or {}).get("channel", "")
        if not os.path.exists(video_path):
            return PublishResult(self.platform, status="error", detail="video yok")

        meta = build_metadata("youtube", job, privacy=(credentials or {}).get("privacy", ""))
        token = access_token(channel)
        snippet = {
            "snippet": {
                "title": meta["title"], "description": meta["description"],
                "tags": meta["tags"], "categoryId": meta["categoryId"],
            },
            "status": {
                "privacyStatus": meta["privacyStatus"],
                "selfDeclaredMadeForKids": False,
            },
        }
        size = os.path.getsize(video_path)
        # 1) Resumable oturum baslat
        init = requests.post(
            UPLOAD_URL,
            headers={"Authorization": f"Bearer {token}",
                     "Content-Type": "application/json; charset=UTF-8",
                     "X-Upload-Content-Type": "video/*",
                     "X-Upload-Content-Length": str(size)},
            data=json.dumps(snippet), timeout=60)
        if init.status_code not in (200, 201):
            raise PublishError(f"YouTube init hatasi {init.status_code}: {init.text[:200]}")
        location = init.headers.get("Location")
        if not location:
            raise PublishError("YouTube resumable Location dondurmedi")

        # 2) Video baytlarini yukle
        with open(video_path, "rb") as f:
            up = requests.put(
                location,
                headers={"Authorization": f"Bearer {token}",
                         "Content-Type": "video/*", "Content-Length": str(size)},
                data=f, timeout=600)
        if up.status_code not in (200, 201):
            raise PublishError(f"YouTube upload hatasi {up.status_code}: {up.text[:200]}")
        vid = up.json().get("id", "")
        log.info("YouTube yuklendi: %s (%s)", vid, meta["privacyStatus"])
        return PublishResult(self.platform, video_id=vid,
                             url=f"https://youtube.com/shorts/{vid}", status="uploaded")
