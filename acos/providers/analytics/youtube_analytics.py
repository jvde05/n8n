"""YouTube analytics provider.

- Temel metrikler (views/likes/comments): Data API videos.list (OAuth ile).
- Derin metrikler (averageViewDuration, averageViewPercentage): YouTube Analytics
  API (kanal sahibi OAuth). Kimlik yoksa bu kisim atlanir.

Ayni YT OAuth kimliklerini (refresh token) kullanir.
"""
from ...errors import ProviderError
from ...interfaces import AnalyticsProvider
from ...logging_utils import get_logger
from ..publish.google_oauth import access_token

log = get_logger("analytics.youtube")
DATA_API = "https://www.googleapis.com/youtube/v3/videos"
ANALYTICS_API = "https://youtubeanalytics.googleapis.com/v2/reports"


class YouTubeAnalytics(AnalyticsProvider):
    def __init__(self, channel: str = ""):
        self.channel = channel

    def fetch_video_stats(self, video_id: str) -> dict:
        import requests  # lazy

        token = access_token(self.channel)
        r = requests.get(DATA_API, params={
            "part": "statistics", "id": video_id}, headers={
            "Authorization": f"Bearer {token}"}, timeout=30)
        if r.status_code != 200:
            raise ProviderError(f"YouTube stats hatasi {r.status_code}: {r.text[:200]}")
        items = r.json().get("items", [])
        if not items:
            return {"video_id": video_id, "found": False}
        s = items[0].get("statistics", {})
        out = {
            "video_id": video_id,
            "found": True,
            "views": int(s.get("viewCount", 0)),
            "likes": int(s.get("likeCount", 0)),
            "comments": int(s.get("commentCount", 0)),
        }
        out.update(self._deep_metrics(video_id, token))
        return out

    def _deep_metrics(self, video_id: str, token: str) -> dict:
        """AVD ve ortalama izlenme yuzdesi — kanal sahibi yetkisi gerektirir."""
        import requests  # lazy
        try:
            r = requests.get(ANALYTICS_API, params={
                "ids": "channel==MINE",
                "metrics": "averageViewDuration,averageViewPercentage,views",
                "filters": f"video=={video_id}",
                "startDate": "2005-01-01", "endDate": "2035-01-01",
            }, headers={"Authorization": f"Bearer {token}"}, timeout=30)
            if r.status_code != 200:
                return {}
            rows = r.json().get("rows", [])
            if not rows:
                return {}
            avd, avp, _views = rows[0][0], rows[0][1], rows[0][2]
            return {"avd_seconds": float(avd), "avg_view_pct": float(avp)}
        except Exception as exc:  # noqa: BLE001
            log.debug("Derin metrik atlandi: %s", exc)
            return {}
