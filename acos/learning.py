"""Self-learning — performans verisinden 'kazanan desenleri' cikarir.

Cikti, retention prompt'una enjekte edilen kisa bir 'insights' metnidir; boylece
sistem zamanla kendi en iyi videolarini taklit etmeyi ogrenir.
"""
import json
import os
from collections import Counter
from typing import List, Optional

from .logging_utils import get_logger
from .store import Store

log = get_logger("learning")


def _insights_path(channel: str) -> str:
    base = os.environ.get("ACOS_INSIGHTS_DIR", "/data/insights")
    os.makedirs(base, exist_ok=True)
    slug = "".join(c if c.isalnum() else "_" for c in (channel or "global")).strip("_")
    return os.path.join(base, f"{slug}.txt")


def compute_insights(store: Store, channel: str = "", min_videos: int = 5) -> str:
    rows = store.top_performers(channel=channel, limit=20, metric="views")
    if len(rows) < min_videos:
        return ""

    top = rows[: max(5, len(rows) // 3)]  # en iyi ~1/3
    voices = Counter(r["voice"] for r in top if r["voice"])
    word_counts = [r["n_words"] for r in top if r["n_words"]]
    kw_counter: Counter = Counter()
    for r in top:
        try:
            for k in json.loads(r["keywords"] or "[]"):
                kw_counter[str(k).lower()] += 1
        except json.JSONDecodeError:
            pass

    lines = ["LEARNED PATTERNS FROM THIS CHANNEL'S BEST-PERFORMING VIDEOS "
             "(replicate what works):"]
    best_hooks = [r["hook"] or r["title"] for r in top[:5] if (r["hook"] or r["title"])]
    if best_hooks:
        lines.append("- High-performing hook styles:")
        lines += [f"    * {h}" for h in best_hooks]
    if voices:
        lines.append(f"- Best voice(s): {', '.join(v for v, _ in voices.most_common(2))}")
    if word_counts:
        avg = sum(word_counts) // len(word_counts)
        lines.append(f"- Ideal narration length: ~{avg} words")
    if kw_counter:
        lines.append("- Visual themes that perform: "
                     + ", ".join(k for k, _ in kw_counter.most_common(6)))
    return "\n".join(lines)


def update_insights(store: Store, channel: str = "") -> str:
    text = compute_insights(store, channel)
    if text:
        with open(_insights_path(channel), "w", encoding="utf-8") as f:
            f.write(text)
        log.info("Insights guncellendi (%s)", channel or "global")
    return text


def load_insights(channel: str = "") -> Optional[str]:
    p = _insights_path(channel)
    if os.path.exists(p):
        return open(p, encoding="utf-8").read()
    return None
