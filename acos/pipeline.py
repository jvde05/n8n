"""Pipeline orkestratoru — bilesenleri birbirine baglar.

Iki giris noktasi paylasir:
- produce_video(job, workdir): TTS + Video + Render (n8n bu adimi cagirir,
  senaryoyu kendi uretir).
- run_job(cfg, topic, workdir): LLM (retention prompt) + produce_video,
  standalone uctan uca uretim.
"""
import json
import os
import time
from typing import List, Optional

from .config import ChannelConfig
from .interfaces import TTSResult
from .logging_utils import get_logger
from . import registry
from .prompts import retention

log = get_logger("pipeline")


def _new_workdir(base: str = "/data/jobs") -> str:
    job_id = f"{int(time.time())}-{os.getpid()}"
    path = os.path.join(base, job_id)
    os.makedirs(path, exist_ok=True)
    return path


def produce_video(job: dict, workdir: str, cfg: Optional[ChannelConfig] = None) -> str:
    """Hazir bir senaryo job'undan (narration, keywords, voice) video uretir."""
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
    out = render.assemble(workdir, tts_res, clips, job)
    return out


def run_job(cfg: ChannelConfig, topic: str, workdir: Optional[str] = None,
            trends: Optional[List[str]] = None) -> dict:
    """Uctan uca: senaryo uret -> video uret. Job + cikti yolunu dondurur."""
    workdir = workdir or _new_workdir()
    llm = registry.make_llm(cfg)

    user = retention.build_user_prompt(topic, cfg.niche, cfg.language, trends)
    raw = llm.generate(retention.SYSTEM, user, max_tokens=1200)
    pkg = retention.parse_script(raw, voice=cfg.voice, language=cfg.language)
    job = pkg.to_job()

    with open(os.path.join(workdir, "job.json"), "w", encoding="utf-8") as f:
        json.dump(job, f, ensure_ascii=False, indent=2)

    out = produce_video(job, workdir, cfg)
    return {"workdir": workdir, "output": out, "job": job}
