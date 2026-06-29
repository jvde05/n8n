"""Pexels stok video provider'i — ucretsiz dikey klipler.

En yuksek cozunurluklu dikey dosyayi secer (upscale'den kacinir).
"""
import json
import os
import urllib.parse
import urllib.request
from typing import List

from ...errors import VideoSourceError
from ...interfaces import VideoProvider
from ...logging_utils import get_logger
from ...retry import retry

log = get_logger("video.pexels")
SEARCH_URL = "https://api.pexels.com/videos/search?"


class PexelsProvider(VideoProvider):
    def __init__(self, api_key: str = ""):
        self.api_key = api_key or os.environ.get("PEXELS_API_KEY", "")

    def fetch_clips(self, keywords: List[str], workdir: str,
                    want: int = 6, min_width: int = 1080) -> List[str]:
        if not self.api_key:
            log.warning("PEXELS_API_KEY yok — stok video atlaniyor (duz arka plan kullanilacak)")
            return []
        clips: List[str] = []
        for kw in keywords:
            for url in self._search(kw, min_width, per_keyword=2):
                dst = os.path.join(workdir, f"raw_{len(clips)}.mp4")
                if self._download(url, dst):
                    clips.append(dst)
            if len(clips) >= want:
                break
        log.info("%d stok klip indirildi (%d anahtar kelime)", len(clips), len(keywords))
        return clips

    @retry(times=2, base_delay=2.0, exceptions=(urllib.error.URLError,))
    def _search(self, keyword: str, min_width: int, per_keyword: int) -> List[str]:
        url = SEARCH_URL + urllib.parse.urlencode({
            "query": keyword, "orientation": "portrait",
            "size": "large", "per_page": 12,
        })
        req = urllib.request.Request(url, headers={"Authorization": self.api_key})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.load(resp)
        out: List[str] = []
        for v in data.get("videos", []):
            files = [f for f in v.get("video_files", [])
                     if (f.get("height") or 0) >= (f.get("width") or 0)]
            hd = [f for f in files if (f.get("width") or 0) >= min_width]
            pool = hd or files
            pool.sort(key=lambda f: (f.get("width") or 0) * (f.get("height") or 0),
                      reverse=True)
            if pool:
                out.append(pool[0]["link"])
            if len(out) >= per_keyword:
                break
        return out

    def _download(self, url: str, dst: str) -> bool:
        try:
            urllib.request.urlretrieve(url, dst)
            return os.path.getsize(dst) > 1000
        except Exception as exc:  # noqa: BLE001
            log.warning("Indirme hatasi: %s", exc)
            return False
