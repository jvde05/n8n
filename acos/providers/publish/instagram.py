"""Instagram Reels yukleyici (Graph API).

ONEMLI: Instagram Graph API yerel dosya kabul ETMEZ; videonun PUBLIC bir URL'de
barindirilmasi gerekir. Bu yuzden job icinde 'hosted_url' beklenir (orn. videoyu
bir S3/CDN/sunucuya koyup URL ver). Yoksa anlamli bir hata doner.

Gereken: IG Business hesabi + FB app. Kimlikler (kanal bazli olabilir):
  IG_USER_ID, IG_ACCESS_TOKEN
"""
import time

from ...credentials import require
from ...errors import PublishError
from ...interfaces import Publisher, PublishResult
from ...logging_utils import get_logger
from ...platforms import build_metadata

log = get_logger("publish.instagram")
GRAPH = "https://graph.facebook.com/v19.0"


class InstagramPublisher(Publisher):
    platform = "instagram"

    def publish(self, video_path: str, job: dict, credentials: dict) -> PublishResult:
        import requests  # lazy

        channel = (credentials or {}).get("channel", "")
        hosted_url = job.get("hosted_url") or (credentials or {}).get("hosted_url")
        if not hosted_url:
            return PublishResult(
                self.platform, status="skipped",
                detail="Instagram public video URL ister; job['hosted_url'] saglanmadi")

        ig_user = require("IG_USER_ID", channel)
        token = require("IG_ACCESS_TOKEN", channel)
        meta = build_metadata("instagram", job)

        # 1) Konteyner olustur
        c = requests.post(f"{GRAPH}/{ig_user}/media", data={
            "media_type": "REELS", "video_url": hosted_url,
            "caption": meta["caption"], "access_token": token,
        }, timeout=60)
        if c.status_code != 200:
            raise PublishError(f"IG konteyner hatasi {c.status_code}: {c.text[:200]}")
        creation_id = c.json().get("id")

        # 2) Hazir olana kadar bekle
        for _ in range(20):
            s = requests.get(f"{GRAPH}/{creation_id}", params={
                "fields": "status_code", "access_token": token}, timeout=30)
            if s.json().get("status_code") == "FINISHED":
                break
            time.sleep(5)

        # 3) Yayinla
        p = requests.post(f"{GRAPH}/{ig_user}/media_publish", data={
            "creation_id": creation_id, "access_token": token}, timeout=60)
        if p.status_code != 200:
            raise PublishError(f"IG yayin hatasi {p.status_code}: {p.text[:200]}")
        media_id = p.json().get("id", "")
        log.info("Instagram Reels yayinlandi: %s", media_id)
        return PublishResult(self.platform, video_id=media_id, status="uploaded")
