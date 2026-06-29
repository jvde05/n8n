"""Tum ACOS hatalari icin ortak hiyerarsi (hata yonetimini netlestirir)."""


class ACOSError(Exception):
    """Tum ACOS hatalarinin tabani."""


class ConfigError(ACOSError):
    """Eksik/hatali yapilandirma."""


class ProviderError(ACOSError):
    """Bir provider (LLM/TTS/Video/...) calisirken hata."""


class LLMError(ProviderError):
    pass


class TTSError(ProviderError):
    pass


class VideoSourceError(ProviderError):
    pass


class RenderError(ProviderError):
    pass


class PublishError(ProviderError):
    pass


class TrendError(ProviderError):
    pass
