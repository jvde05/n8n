"""Provider fabrikasi — config'teki isimleri somut siniflara baglar.

Yeni bir saglayici eklemek = buraya bir satir. Pipeline degismez.
"""
from .config import ChannelConfig, RenderOptions
from .errors import ConfigError
from .interfaces import LLMProvider, TTSProvider, VideoProvider, RenderEngine, Publisher


def make_llm(cfg: ChannelConfig) -> LLMProvider:
    name = cfg.providers.llm
    if name == "anthropic":
        from .providers.llm.anthropic_provider import AnthropicProvider
        return AnthropicProvider(model=cfg.llm_model)
    raise ConfigError(f"Bilinmeyen LLM provider: {name}")


def make_tts(cfg: ChannelConfig) -> TTSProvider:
    name = cfg.providers.tts
    if name == "edge":
        from .providers.tts.edge_provider import EdgeTTSProvider
        return EdgeTTSProvider(words_per_caption=cfg.render.words_per_caption)
    raise ConfigError(f"Bilinmeyen TTS provider: {name}")


def make_video(cfg: ChannelConfig) -> VideoProvider:
    name = cfg.providers.video
    if name == "pexels":
        from .providers.video.pexels_provider import PexelsProvider
        return PexelsProvider()
    raise ConfigError(f"Bilinmeyen video provider: {name}")


def make_render(cfg: ChannelConfig) -> RenderEngine:
    name = cfg.providers.render
    if name == "ffmpeg":
        from .providers.render.ffmpeg_engine import FFmpegRenderEngine
        return FFmpegRenderEngine(options=cfg.render)
    raise ConfigError(f"Bilinmeyen render engine: {name}")


def make_publisher(cfg: ChannelConfig) -> Publisher:
    name = cfg.providers.publish
    from .providers.publish.publishers import (
        NoopPublisher, YouTubePublisher, TikTokPublisher, InstagramPublisher)
    table = {
        "noop": NoopPublisher, "youtube": YouTubePublisher,
        "tiktok": TikTokPublisher, "instagram": InstagramPublisher,
    }
    cls = table.get(name)
    if not cls:
        raise ConfigError(f"Bilinmeyen publisher: {name}")
    return cls()
