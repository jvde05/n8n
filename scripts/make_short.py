#!/usr/bin/env python3
"""n8n koprusu (geriye donuk uyumlu).

n8n 'Video Render' node'u bunu cagirir:  python3 /scripts/make_short.py <job_dir>
Gercek is artik moduler ACOS cekirdeginde (acos/ paketi).

job.json icermeli: { "narration", "keywords", "voice", "title", ... }
Cikti: <job_dir>/output.mp4
"""
import json
import os
import sys

# ACOS paketini bul (Docker'da PYTHONPATH=/app; yerelde repo kokunu ekle).
sys.path.insert(0, "/app")
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from acos.pipeline import produce_video  # noqa: E402


def main() -> int:
    if len(sys.argv) < 2:
        print("kullanim: make_short.py <job_dir>", file=sys.stderr)
        return 2
    job_dir = sys.argv[1]
    with open(os.path.join(job_dir, "job.json"), encoding="utf-8") as f:
        job = json.load(f)
    out = produce_video(job, job_dir)
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
