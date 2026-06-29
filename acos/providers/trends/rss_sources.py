"""Trend kefor kaynaklari — anahtar GEREKTIRMEYEN, ucretsiz RSS tabanli.

- GoogleTrendsRSS: gunluk yukselen aramalar (geo bazli)
- RedditRSS: nise uygun subreddit'lerin gunluk en iyileri

Statik konu listesi yerine bunlar kullanilarak viral potansiyeli yuksek,
guncel konular kesfedilir. LLM bu ham trendleri alip nise gore en iyi acilari secer.
"""
import urllib.request
import xml.etree.ElementTree as ET
from typing import List

from ...interfaces import Trend, TrendSource
from ...logging_utils import get_logger

log = get_logger("trends.rss")
_UA = {"User-Agent": "Mozilla/5.0 (ACOS trend discovery)"}


def _get(url: str, timeout: int = 20) -> str:
    req = urllib.request.Request(url, headers=_UA)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", "ignore")


def _titles_from_rss(xml_text: str) -> List[str]:
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return []
    out = []
    for item in root.iter("item"):
        t = item.findtext("title")
        if t:
            out.append(t.strip())
    return out


class GoogleTrendsRSS(TrendSource):
    name = "google_trends"

    def __init__(self, geo: str = "US"):
        self.geo = geo

    def fetch(self, niche: str = "", limit: int = 20) -> List[Trend]:
        url = (f"https://trends.google.com/trends/trendingsearches/daily/rss?geo={self.geo}")
        try:
            titles = _titles_from_rss(_get(url))
        except Exception as exc:  # noqa: BLE001
            log.warning("Google Trends alinamadi: %s", exc)
            return []
        return [Trend(title=t, source=self.name, score=1.0 - i / max(1, len(titles)))
                for i, t in enumerate(titles[:limit])]


class RedditRSS(TrendSource):
    name = "reddit"

    def __init__(self, subreddits: List[str] = None, period: str = "day"):
        self.subreddits = subreddits or ["todayilearned", "Damnthatsinteresting"]
        self.period = period

    def fetch(self, niche: str = "", limit: int = 20) -> List[Trend]:
        out: List[Trend] = []
        per_sub = max(1, limit // max(1, len(self.subreddits)))
        for sub in self.subreddits:
            url = f"https://www.reddit.com/r/{sub}/top/.rss?t={self.period}&limit={per_sub}"
            try:
                titles = _titles_from_rss(_get(url))
            except Exception as exc:  # noqa: BLE001
                log.warning("Reddit r/%s alinamadi: %s", sub, exc)
                continue
            for i, t in enumerate(titles[:per_sub]):
                out.append(Trend(title=t, source=f"reddit/{sub}",
                                 score=1.0 - i / max(1, per_sub)))
        return out[:limit]


_REGISTRY = {"google_trends": GoogleTrendsRSS, "reddit": RedditRSS}


def aggregate(source_names: List[str], subreddits: List[str] = None,
              geo: str = "US", limit: int = 30) -> List[Trend]:
    """Secili kaynaklardan trendleri toplar, skora gore siralar."""
    trends: List[Trend] = []
    for name in source_names:
        cls = _REGISTRY.get(name)
        if not cls:
            log.warning("Bilinmeyen trend kaynagi: %s", name)
            continue
        src = cls(subreddits=subreddits) if name == "reddit" else cls(geo=geo)
        trends.extend(src.fetch(limit=limit))
    trends.sort(key=lambda t: t.score, reverse=True)
    return trends[:limit]
