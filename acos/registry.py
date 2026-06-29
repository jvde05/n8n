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


def make_publisher(name: str) -> Publisher:
    """Platform adina gore yayinci dondurur (youtube/tiktok/instagram/noop)."""
    if name == "noop":
        from .providers.publish.publishers import NoopPublisher
        return NoopPublisher()
    if name == "youtube":
        from .providers.publish.youtube_api import YouTubeAPIPublisher
        return YouTubeAPIPublisher()
    if name == "tiktok":
        from .providers.publish.tiktok import TikTokPublisher
        return TikTokPublisher()
    if name == "instagram":
        from .providers.publish.instagram import InstagramPublisher
        return InstagramPublisher()
    raise ConfigError(f"Bilinmeyen publisher: {name}")


def make_analytics(cfg: ChannelConfig, channel: str = ""):
    name = cfg.providers.analytics
    if name == "youtube":
        from .providers.analytics.youtube_analytics import YouTubeAnalytics
        return YouTubeAnalytics(channel=channel or cfg.name)
    raise ConfigError(f"Bilinmeyen analytics provider: {name}")
