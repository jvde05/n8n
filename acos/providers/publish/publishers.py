"""Yukleme yapmayan yayinci — standalone test / sadece-render senaryosu icin.

Gercek yukleyiciler ayri modullerde:
  youtube_api.YouTubeAPIPublisher, tiktok.TikTokPublisher, instagram.InstagramPublisher
"""
from ...interfaces import Publisher, PublishResult
from ...logging_utils import get_logger

log = get_logger("publish.noop")


class NoopPublisher(Publisher):
    """Yukleme yapmaz; render edilen dosyayi birakir (n8n yukler veya elle)."""
    platform = "noop"

    def publish(self, video_path: str, job: dict, credentials: dict) -> PublishResult:
        log.info("NoopPublisher: video hazir -> %s", video_path)
        return PublishResult(platform="noop", status="rendered", url=video_path)
