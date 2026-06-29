"""ACOS komut satiri arayuzu.

  python -m acos.cli render <job_dir>           # n8n koprusu: job.json -> output.mp4
  python -m acos.cli run --channel ch.yaml [--topic "..."]   # uctan uca uretim
  python -m acos.cli discover --channel ch.yaml [--limit 20] # trend kesfi
"""
import argparse
import json
import os
import random
import sys

from .config import ChannelConfig, load_channel
from .logging_utils import get_logger
from .pipeline import produce_video, run_job
from .providers.trends import rss_sources

log = get_logger("cli")


def _cmd_render(args) -> int:
    job_path = os.path.join(args.job_dir, "job.json")
    with open(job_path, encoding="utf-8") as f:
        job = json.load(f)
    out = produce_video(job, args.job_dir)
    print(out)
    return 0


def _cmd_discover(args) -> int:
    cfg = load_channel(args.channel) if args.channel else ChannelConfig()
    trends = rss_sources.aggregate(
        cfg.trend_sources, subreddits=cfg.subreddits,
        geo=args.geo, limit=args.limit)
    for t in trends:
        print(f"[{t.score:.2f}] {t.source}: {t.title}")
    return 0


def _cmd_run(args) -> int:
    cfg = load_channel(args.channel)
    topic = args.topic
    trend_titles = None
    if cfg.trend_sources and (args.use_trends or not topic):
        trends = rss_sources.aggregate(cfg.trend_sources, subreddits=cfg.subreddits,
                                       geo=args.geo, limit=20)
        trend_titles = [t.title for t in trends]
        if not topic and trend_titles:
            topic = trend_titles[0]
    if not topic:
        topic = random.choice(cfg.topics) if cfg.topics else cfg.niche
    log.info("Konu: %s", topic)
    result = run_job(cfg, topic, trends=trend_titles)
    print(json.dumps({"output": result["output"], "title": result["job"]["title"]},
                     ensure_ascii=False))
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="acos")
    sub = p.add_subparsers(dest="cmd", required=True)

    pr = sub.add_parser("render", help="job.json -> output.mp4 (n8n koprusu)")
    pr.add_argument("job_dir")
    pr.set_defaults(func=_cmd_render)

    pd = sub.add_parser("discover", help="trend kesfi")
    pd.add_argument("--channel")
    pd.add_argument("--geo", default="US")
    pd.add_argument("--limit", type=int, default=20)
    pd.set_defaults(func=_cmd_discover)

    pn = sub.add_parser("run", help="uctan uca uretim")
    pn.add_argument("--channel", required=True)
    pn.add_argument("--topic", default="")
    pn.add_argument("--use-trends", action="store_true")
    pn.add_argument("--geo", default="US")
    pn.set_defaults(func=_cmd_run)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
