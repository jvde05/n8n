"""Kanal/marka yapilandirmasi. YAML veya JSON'dan yuklenir.

Her kanal kendi nis, dil, ses, platform ve provider secimini tasir —
boylece 3-4 (veya 50) kanali tek kod tabaniyla yonetebiliriz.
"""
from dataclasses import dataclass, field, asdict
from typing import List
import json
import os

from .errors import ConfigError


@dataclass
class ProviderSelection:
    llm: str = "anthropic"
    tts: str = "edge"
    video: str = "pexels"
    render: str = "ffmpeg"
    publish: str = "youtube"


@dataclass
class RenderOptions:
    width: int = 1080
    height: int = 1920
    fps: int = 30
    crf: int = 18
    preset: str = "slow"
    motion: bool = True          # Ken Burns / dinamik zoom
    cinematic: bool = True       # sinematik renk + keskinlik
    loudnorm: bool = True        # ses normalizasyonu (-14 LUFS)
    words_per_caption: int = 3
    font: str = "DejaVu Sans"
    clip_seconds: int = 6
    bgm_path: str = "/scripts/assets/bgm.mp3"
    bgm_volume: float = 0.12


@dataclass
class ChannelConfig:
    name: str = "Channel"
    niche: str = "interesting facts"
    language: str = "en"
    voice: str = "en-US-AriaNeural"
    platforms: List[str] = field(default_factory=lambda: ["youtube"])
    topics: List[str] = field(default_factory=list)        # statik yedek
    trend_sources: List[str] = field(default_factory=lambda: ["google_trends", "reddit"])
    subreddits: List[str] = field(default_factory=lambda: ["todayilearned", "Damnthatsinteresting"])
    llm_model: str = "claude-haiku-4-5-20251001"
    providers: ProviderSelection = field(default_factory=ProviderSelection)
    render: RenderOptions = field(default_factory=RenderOptions)

    @staticmethod
    def from_dict(d: dict) -> "ChannelConfig":
        d = dict(d or {})
        prov = ProviderSelection(**(d.pop("providers", {}) or {}))
        rend = RenderOptions(**(d.pop("render", {}) or {}))
        return ChannelConfig(providers=prov, render=rend, **d)

    def to_dict(self) -> dict:
        return asdict(self)


def load_channel(path: str) -> ChannelConfig:
    if not os.path.exists(path):
        raise ConfigError(f"Kanal yapilandirmasi bulunamadi: {path}")
    text = open(path, encoding="utf-8").read()
    if path.endswith((".yaml", ".yml")):
        try:
            import yaml  # type: ignore
        except ImportError as exc:
            raise ConfigError("YAML icin 'pyyaml' gerekli (pip install pyyaml)") from exc
        data = yaml.safe_load(text)
    else:
        data = json.loads(text)
    return ChannelConfig.from_dict(data)
