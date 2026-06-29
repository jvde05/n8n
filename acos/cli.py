"""ACOS komut satiri arayuzu.

  python -m acos.cli render <job_dir>                         # n8n koprusu
  python -m acos.cli run --channel ch.yaml [--topic ..] [--publish]
  python -m acos.cli publish --channel ch.yaml --video out.mp4 --job job.json
  python -m acos.cli discover --channel ch.yaml [--limit 20]
  python -m acos.cli sync-stats --channel ch.yaml            # metrikleri cek
  python -m acos.cli learn --channel ch.yaml                 # insights uret
"""
import argparse
import json
import os
import random
import sys

from .config import ChannelConfig, load_channel
from .logging_utils import get_logger
from . import pipeline
from .providers.trends import rss_sources

log = get_logger("cli")


def _cmd_render(args) -> int:
    with open(os.path.join(args.job_dir, "job.json"), encoding="utf-8") as f:
        job = json.load(f)
    print(pipeline.produce_video(job, args.job_dir))
    return 0


def _cmd_discover(args) -> int:
    cfg = load_channel(args.channel) if args.channel else ChannelConfig()
    trends = rss_sources.aggregate(cfg.trend_sources, subreddits=cfg.subreddits,
                                   geo=args.geo, limit=args.limit)
    for t in trends:
        print(f"[{t.score:.2f}] {t.source}: {t.title}")
    return 0


def _resolve_topic(cfg, args):
    trend_titles = None
    topic = args.topic
    if cfg.trend_sources and (args.use_trends or not topic):
        trends = rss_sources.aggregate(cfg.trend_sources, subreddits=cfg.subreddits,
                                       geo=args.geo, limit=20)
        trend_titles = [t.title for t in trends]
        if not topic and trend_titles:
            topic = trend_titles[0]
    if not topic:
        topic = random.choice(cfg.topics) if cfg.topics else cfg.niche
    return topic, trend_titles


def _cmd_run(args) -> int:
    cfg = load_channel(args.channel)
    topic, trend_titles = _resolve_topic(cfg, args)
    log.info("Konu: %s", topic)
    result = pipeline.run_job(cfg, topic, trends=trend_titles, publish=args.publish)
    print(json.dumps({"output": result["output"], "title": result["job"]["title"],
                      "publish": result["publish"]}, ensure_ascii=False, indent=2))
    return 0


def _cmd_publish(args) -> int:
    cfg = load_channel(args.channel)
    with open(args.job, encoding="utf-8") as f:
        job = json.load(f)
    results = pipeline.publish_all(cfg, args.video, job)
    print(json.dumps([r.__dict__ for r in results], ensure_ascii=False, indent=2))
    return 0


def _cmd_sync_stats(args) -> int:
    cfg = load_channel(args.channel)
    print(json.dumps({"updated": pipeline.sync_stats(cfg)}))
    return 0


def _cmd_learn(args) -> int:
    cfg = load_channel(args.channel)
    text = pipeline.learn(cfg)
    print(text or "(yeterli veri yok — once daha cok video yayinla ve sync-stats calistir)")
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="acos")
    sub = p.add_subparsers(dest="cmd", required=True)

    pr = sub.add_parser("render"); pr.add_argument("job_dir"); pr.set_defaults(func=_cmd_render)

    pd = sub.add_parser("discover")
    pd.add_argument("--channel"); pd.add_argument("--geo", default="US")
    pd.add_argument("--limit", type=int, default=20); pd.set_defaults(func=_cmd_discover)

    pn = sub.add_parser("run")
    pn.add_argument("--channel", required=True); pn.add_argument("--topic", default="")
    pn.add_argument("--use-trends", action="store_true"); pn.add_argument("--geo", default="US")
    pn.add_argument("--publish", action="store_true"); pn.set_defaults(func=_cmd_run)

    pp = sub.add_parser("publish")
    pp.add_argument("--channel", required=True); pp.add_argument("--video", required=True)
    pp.add_argument("--job", required=True); pp.set_defaults(func=_cmd_publish)

    ps = sub.add_parser("sync-stats")
    ps.add_argument("--channel", required=True); ps.set_defaults(func=_cmd_sync_stats)

    pl = sub.add_parser("learn")
    pl.add_argument("--channel", required=True); pl.set_defaults(func=_cmd_learn)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
