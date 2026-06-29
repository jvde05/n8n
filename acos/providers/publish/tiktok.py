"""TikTok yukleyici (Content Posting API, FILE_UPLOAD).

Gereken: onayli bir TikTok developer app + kullanici yetkisi.
Kimlik (kanal bazli olabilir):  TT_ACCESS_TOKEN
Not: Sandbox/inceleme asamasinda gizlilik SELF_ONLY olmak zorundadir.
"""
import os

from ...credentials import require
from ...errors import PublishError
from ...interfaces import Publisher, PublishResult
from ...logging_utils import get_logger
from ...platforms import build_metadata

log = get_logger("publish.tiktok")
INIT_URL = "https://open.tiktokapis.com/v2/post/publish/video/init/"


class TikTokPublisher(Publisher):
    platform = "tiktok"

    def publish(self, video_path: str, job: dict, credentials: dict) -> PublishResult:
        import requests  # lazy

        channel = (credentials or {}).get("channel", "")
        token = require("TT_ACCESS_TOKEN", channel)
        meta = build_metadata("tiktok", job, privacy=(credentials or {}).get("privacy", ""))
        size = os.path.getsize(video_path)

        init = requests.post(
            INIT_URL,
            headers={"Authorization": f"Bearer {token}",
                     "Content-Type": "application/json; charset=UTF-8"},
            json={
                "post_info": {
                    "title": meta["caption"],
                    "privacy_level": meta["privacy"],
                    "disable_comment": False,
                },
                "source_info": {
                    "source": "FILE_UPLOAD", "video_size": size,
                    "chunk_size": size, "total_chunk_count": 1,
                },
            }, timeout=60)
        if init.status_code != 200:
            raise PublishError(f"TikTok init hatasi {init.status_code}: {init.text[:200]}")
        d = init.json().get("data", {})
        publish_id = d.get("publish_id", "")
        upload_url = d.get("upload_url")
        if not upload_url:
            raise PublishError(f"TikTok upload_url yok: {init.text[:200]}")

        with open(video_path, "rb") as f:
            up = requests.put(
                upload_url,
                headers={"Content-Type": "video/mp4",
                         "Content-Range": f"bytes 0-{size - 1}/{size}",
                         "Content-Length": str(size)},
                data=f, timeout=600)
        if up.status_code not in (200, 201):
            raise PublishError(f"TikTok upload hatasi {up.status_code}: {up.text[:200]}")
        log.info("TikTok'a gonderildi: %s", publish_id)
        return PublishResult(self.platform, video_id=publish_id, status="uploaded",
                             detail="islem TikTok tarafinda tamamlanir")
