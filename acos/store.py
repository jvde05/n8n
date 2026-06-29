"""Performans veritabani (SQLite) — uretilen videolar ve metrikleri.

Self-learning'in temeli: ne urettik, nasil performans gosterdi.
Veriden 'kazanan desenler' cikarip promptlari gelistirmek icin kullanilir.
"""
import json
import os
import sqlite3
import time
from typing import List, Optional

from .logging_utils import get_logger

log = get_logger("store")

_SCHEMA = """
CREATE TABLE IF NOT EXISTS videos (
    pk INTEGER PRIMARY KEY AUTOINCREMENT,
    channel TEXT, platform TEXT, video_id TEXT,
    title TEXT, hook TEXT, voice TEXT, language TEXT,
    n_words INTEGER, keywords TEXT, hashtags TEXT,
    created_at REAL,
    UNIQUE(platform, video_id)
);
CREATE TABLE IF NOT EXISTS stats (
    video_pk INTEGER PRIMARY KEY,
    fetched_at REAL,
    views INTEGER DEFAULT 0, likes INTEGER DEFAULT 0, comments INTEGER DEFAULT 0,
    avd_seconds REAL, avg_view_pct REAL,
    FOREIGN KEY(video_pk) REFERENCES videos(pk)
);
"""


class Store:
    def __init__(self, path: str = ""):
        self.path = path or os.environ.get("ACOS_DB", "/data/acos.db")
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(_SCHEMA)
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()

    # ----------------------------------------------------------- yazma
    def record_video(self, channel: str, platform: str, video_id: str, job: dict) -> int:
        narration = job.get("narration", "") or ""
        row = (
            channel, platform, video_id,
            job.get("title", ""), job.get("hook", ""), job.get("voice", ""),
            job.get("language", ""), len(narration.split()),
            json.dumps(job.get("keywords", []), ensure_ascii=False),
            json.dumps(job.get("tags", []), ensure_ascii=False),
            time.time(),
        )
        cur = self.conn.execute(
            "INSERT OR IGNORE INTO videos "
            "(channel,platform,video_id,title,hook,voice,language,n_words,keywords,hashtags,created_at) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?)", row)
        self.conn.commit()
        # rowcount==0 => zaten vardi (INSERT IGNORE atladi); lastrowid OR IGNORE'da guvenilmez.
        if cur.rowcount and cur.lastrowid:
            return cur.lastrowid
        got = self.conn.execute(
            "SELECT pk FROM videos WHERE platform=? AND video_id=?",
            (platform, video_id)).fetchone()
        return got["pk"] if got else 0

    def upsert_stats(self, video_pk: int, stats: dict) -> None:
        self.conn.execute(
            "INSERT INTO stats (video_pk,fetched_at,views,likes,comments,avd_seconds,avg_view_pct) "
            "VALUES (?,?,?,?,?,?,?) "
            "ON CONFLICT(video_pk) DO UPDATE SET "
            "fetched_at=excluded.fetched_at, views=excluded.views, likes=excluded.likes, "
            "comments=excluded.comments, avd_seconds=excluded.avd_seconds, "
            "avg_view_pct=excluded.avg_view_pct",
            (video_pk, time.time(), stats.get("views", 0), stats.get("likes", 0),
             stats.get("comments", 0), stats.get("avd_seconds"), stats.get("avg_view_pct")))
        self.conn.commit()

    # ----------------------------------------------------------- okuma
    def videos_to_sync(self, platform: str = "youtube",
                       channel: str = "") -> List[sqlite3.Row]:
        q = "SELECT pk, video_id FROM videos WHERE platform=? AND video_id != ''"
        args = [platform]
        if channel:
            q += " AND channel=?"
            args.append(channel)
        return self.conn.execute(q, args).fetchall()

    def top_performers(self, channel: str = "", limit: int = 15,
                       metric: str = "views") -> List[sqlite3.Row]:
        metric = metric if metric in ("views", "avg_view_pct", "avd_seconds") else "views"
        q = (f"SELECT v.*, s.views, s.likes, s.comments, s.avd_seconds, s.avg_view_pct "
             f"FROM videos v JOIN stats s ON s.video_pk=v.pk ")
        args: list = []
        if channel:
            q += "WHERE v.channel=? "
            args.append(channel)
        q += f"ORDER BY COALESCE(s.{metric},0) DESC LIMIT ?"
        args.append(limit)
        return self.conn.execute(q, args).fetchall()
