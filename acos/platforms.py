"""Platform format profilleri ve metadata olusturma.

Ayni icerik paketinden her platforma uygun baslik/caption/hashtag uretir.
Boylece tek senaryo -> YouTube + TikTok + Instagram metadatasi.
"""
import re
from dataclasses import dataclass
from typing import List


@dataclass
class PlatformProfile:
    name: str
    max_title: int
    max_caption: int
    privacy_default: str
    aspect: str = "9:16"


PROFILES = {
    "youtube": PlatformProfile("youtube", max_title=100, max_caption=5000, privacy_default="private"),
    "tiktok": PlatformProfile("tiktok", max_title=2200, max_caption=2200, privacy_default="SELF_ONLY"),
    "instagram": PlatformProfile("instagram", max_title=2200, max_caption=2200, privacy_default="public"),
}


def hashtags_from_tags(tags: List[str], limit: int = 8) -> str:
    out = []
    for t in tags[:limit]:
        clean = re.sub(r"\W+", "", str(t))
        if clean:
            out.append("#" + clean)
    return " ".join(out)


def build_metadata(platform: str, job: dict, privacy: str = "") -> dict:
    """Bir platform icin yukleme metadatasi sozlugu uretir."""
    prof = PROFILES.get(platform, PROFILES["youtube"])
    title = (job.get("title") or "").strip()[: prof.max_title]
    desc = (job.get("description") or "").strip()
    tags = job.get("tags") or []
    hashtags = hashtags_from_tags(tags)
    priv = privacy or prof.privacy_default

    if platform == "youtube":
        body = desc
        if hashtags:
            body += "\n\n" + hashtags
        if "#shorts" not in body.lower():
            body += "\n#shorts"
        return {
            "title": title or "Short",
            "description": body[: prof.max_caption],
            "tags": [str(t) for t in tags][:15],
            "categoryId": str(job.get("categoryId", "22")),
            "privacyStatus": priv,
        }

    # TikTok / Instagram: tek 'caption' alani (baslik + aciklama + hashtag)
    parts = [p for p in [title, desc, hashtags] if p]
    caption = "\n\n".join(parts)[: prof.max_caption]
    return {"caption": caption, "privacy": priv}
