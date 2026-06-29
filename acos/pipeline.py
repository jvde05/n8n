"""Pipeline orkestratoru — bilesenleri birbirine baglar.

Giris noktalari:
- produce_video(job, workdir): TTS + Video + Render (n8n bu adimi cagirir).
- run_job(cfg, topic): LLM (retention + insights) + produce_video [+ publish].
- publish_all(cfg, video, job): kanalin tum platformlarina dagit (+ kayit).
- sync_stats(cfg) / learn(cfg): analytics geri besleme dongusu.
"""
import json
import os
import time
from typing import List, Optional

from .config import ChannelConfig
from .interfaces import PublishResult, TTSResult
from .logging_utils import get_logger
from . import registry
from . import learning
from .prompts import retention

log = get_logger("pipeline")


def _new_workdir(base: str = "/data/jobs") -> str:
    job_id = f"{int(time.time())}-{os.getpid()}"
    path = os.path.join(base, job_id)
    os.makedirs(path, exist_ok=True)
    return path


# --------------------------------------------------------------------------- #
#  Uretim
# --------------------------------------------------------------------------- #
def produce_video(job: dict, workdir: str, cfg: Optional[ChannelConfig] = None) -> str:
    cfg = cfg or ChannelConfig()
    tts = registry.make_tts(cfg)
    video = registry.make_video(cfg)
    render = registry.make_render(cfg)

    narration = (job.get("narration") or job.get("title") or "").strip()
    keywords = job.get("keywords") or [job.get("title", "abstract")]
    voice = job.get("voice") or cfg.voice

    log.info("Uretim basladi: %s", job.get("title", "")[:60])
    tts_res: TTSResult = tts.synthesize(narration, voice, workdir)
    clips = video.fetch_clips(keywords, workdir, want=6, min_width=cfg.render.width)
    return render.assemble(workdir, tts_res, clips, job)


def run_job(cfg: ChannelConfig, topic: str, workdir: Optional[str] = None,
            trends: Optional[List[str]] = None, publish: bool = False) -> dict:
    """Uctan uca: insights+trend ile senaryo uret -> video uret -> [yayinla]."""
    workdir = workdir or _new_workdir()
    llm = registry.make_llm(cfg)

    insights = learning.load_insights(cfg.name)   # self-learning geri beslemesi
    user = retention.build_user_prompt(topic, cfg.niche, cfg.language, trends, insights)
    raw = llm.generate(retention.SYSTEM, user, max_tokens=1200)
    pkg = retention.parse_script(raw, voice=cfg.voice, language=cfg.language)
    job = pkg.to_job()

    with open(os.path.join(workdir, "job.json"), "w", encoding="utf-8") as f:
        json.dump(job, f, ensure_ascii=False, indent=2)

    out = produce_video(job, workdir, cfg)
    result = {"workdir": workdir, "output": out, "job": job, "publish": []}
    if publish:
        result["publish"] = [r.__dict__ for r in publish_all(cfg, out, job)]
    return result


# --------------------------------------------------------------------------- #
#  Cok platform yayini
# --------------------------------------------------------------------------- #
def publish_all(cfg: ChannelConfig, video_path: str, job: dict) -> List[PublishResult]:
    """Kanalin tum platformlarina yukler. Biri patlarsa digerleri devam eder."""
    from .store import Store
    store = Store()
    results: List[PublishResult] = []
    for platform in cfg.platforms:
        try:
            pub = registry.make_publisher(platform)
            res = pub.publish(video_path, job,
                              {"channel": cfg.name, "privacy": cfg.privacy})
        except Exception as exc:  # noqa: BLE001 — bir platform digerlerini engellemez
            log.error("%s yukleme hatasi: %s", platform, exc)
            res = PublishResult(platform=platform, status="error", detail=str(exc))
        results.append(res)
        if res.status == "uploaded" and res.video_id:
            store.record_video(cfg.name, platform, res.video_id, job)
    store.close()
    return results


# --------------------------------------------------------------------------- #
#  Analytics geri besleme dongusu (self-learning)
# --------------------------------------------------------------------------- #
def sync_stats(cfg: ChannelConfig) -> int:
    """Kanalin YouTube videolarinin guncel metriklerini ceker, depoya yazar."""
    from .store import Store
    store = Store()
    analytics = registry.make_analytics(cfg, cfg.name)
    rows = store.videos_to_sync(platform="youtube", channel=cfg.name)
    n = 0
    for row in rows:
        try:
            stats = analytics.fetch_video_stats(row["video_id"])
            if stats.get("found"):
                store.upsert_stats(row["pk"], stats)
                n += 1
        except Exception as exc:  # noqa: BLE001
            log.warning("Stat cekilemedi (%s): %s", row["video_id"], exc)
    store.close()
    log.info("%d video metrigi guncellendi", n)
    return n


def learn(cfg: ChannelConfig) -> str:
    """Performans verisinden insights uretir, prompt'a enjekte edilmek uzere kaydeder."""
    from .store import Store
    store = Store()
    text = learning.update_insights(store, cfg.name)
    store.close()
    return text
