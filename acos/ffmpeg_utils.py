"""Ince ffmpeg/ffprobe yardimcilari."""
import subprocess

from .errors import RenderError
from .logging_utils import get_logger

log = get_logger("ffmpeg")


def run(cmd, check=True):
    log.debug("+ %s", " ".join(str(c) for c in cmd))
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if check and proc.returncode != 0:
        raise RenderError(
            f"Komut basarisiz ({proc.returncode}): {' '.join(str(c) for c in cmd[:3])}...\n"
            f"{proc.stderr[-800:]}"
        )
    return proc


def probe_duration(path: str) -> float:
    proc = run([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", path,
    ])
    try:
        return float((proc.stdout or "0").strip())
    except ValueError:
        return 0.0
