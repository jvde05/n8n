"""Yayinci (Publisher) provider'lari — cok platform icin tek arayuz.

Bugun: YouTube yuklemesi n8n'in YouTube node'u uzerinden yapiliyor (OAuth/kimlik
yonetimi n8n'de). Bu yuzden ACOS standalone modunda video DOSYASINI uretir ve
yuklemeyi n8n'e birakir (NoopPublisher).

Yol haritasi: native uploader'lar (YouTube Data API, TikTok Content Posting API,
Instagram Graph API) ayni Publisher arayuzunu uygulayarak buraya eklenecek;
boylece pipeline degismeden platform eklenebilir.
"""
from ...interfaces import Publisher, PublishResult
from ...logging_utils import get_logger

log = get_logger("publish")


class NoopPublisher(Publisher):
    """Yukleme yapmaz; dosyayi diske birakir (n8n yukler). Standalone test icin."""
    platform = "noop"

    def publish(self, video_path: str, job: dict, credentials: dict) -> PublishResult:
        log.info("NoopPublisher: video hazir, yukleme n8n'e birakildi -> %s", video_path)
        return PublishResult(platform="noop", status="rendered", url=video_path)


class _PlannedPublisher(Publisher):
    """Henuz uygulanmamis platformlar icin acik sozlesme (yol haritasi)."""
    platform = "planned"

    def publish(self, video_path: str, job: dict, credentials: dict) -> PublishResult:
        raise NotImplementedError(
            f"{self.platform} native uploader yol haritasinda. "
            f"Su an yukleme n8n uzerinden yapiliyor."
        )


class YouTubePublisher(_PlannedPublisher):
    platform = "youtube"


class TikTokPublisher(_PlannedPublisher):
    platform = "tiktok"


class InstagramPublisher(_PlannedPublisher):
    platform = "instagram"
