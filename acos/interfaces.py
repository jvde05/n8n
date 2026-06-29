"""Provider arayuzleri (ABC). Her bilesen bu sozlesmeleri uygular,
boylece platform/saglayici bagimsiz, takilip-cikarilabilir olur.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional


# --------------------------------------------------------------------------- #
#  Veri modelleri
# --------------------------------------------------------------------------- #
@dataclass
class Scene:
    """Senaryonun tek bir gorsel/anlatim parcasi."""
    narration: str
    visual_keyword: str
    on_screen_text: str = ""


@dataclass
class ScriptPackage:
    """LLM'in urettigi, retention-odakli tam icerik paketi."""
    title: str
    narration: str            # seslendirilecek tam metin (hook ile baslar)
    keywords: List[str]       # stok video arama terimleri
    description: str = ""
    tags: List[str] = field(default_factory=list)
    hook: str = ""            # ilk 2 saniyenin metni
    cta: str = ""
    loop_line: str = ""       # videoyu basa baglayan kapanis (loop etkisi)
    title_variants: List[str] = field(default_factory=list)  # A/B icin
    scenes: List[Scene] = field(default_factory=list)
    language: str = "en"
    voice: str = "en-US-AriaNeural"

    def to_job(self) -> dict:
        """Render katmaninin okudugu duz job sozlugu."""
        return {
            "title": self.title,
            "narration": self.narration,
            "keywords": self.keywords,
            "description": self.description,
            "tags": self.tags,
            "voice": self.voice,
            "language": self.language,
            "title_variants": self.title_variants,
        }


@dataclass
class Trend:
    title: str
    source: str
    score: float = 0.0
    url: str = ""


@dataclass
class PublishResult:
    platform: str
    video_id: str = ""
    url: str = ""
    status: str = "unknown"


# --------------------------------------------------------------------------- #
#  Provider sozlesmeleri
# --------------------------------------------------------------------------- #
class LLMProvider(ABC):
    @abstractmethod
    def generate(self, system: str, user: str, max_tokens: int = 1024) -> str:
        """Metin uretir (ham string dondurur)."""


class TTSProvider(ABC):
    @abstractmethod
    def synthesize(self, text: str, voice: str, workdir: str) -> "TTSResult":
        """Seslendirme + zaman damgali altyazi uretir."""


@dataclass
class TTSResult:
    audio_path: str
    subtitle_path: Optional[str]
    duration: float


class VideoProvider(ABC):
    @abstractmethod
    def fetch_clips(self, keywords: List[str], workdir: str,
                    want: int = 6, min_width: int = 1080) -> List[str]:
        """Anahtar kelimelere gore ham dikey klipler indirir, yol listesi dondurur."""


class RenderEngine(ABC):
    @abstractmethod
    def assemble(self, workdir: str, tts: "TTSResult",
                 raw_clips: List[str], job: dict) -> str:
        """Ses + klip + altyazidan nihai dikey videoyu uretir; cikti yolunu dondurur."""


class Publisher(ABC):
    platform: str = "base"

    @abstractmethod
    def publish(self, video_path: str, job: dict, credentials: dict) -> PublishResult:
        """Videoyu hedef platforma yukler."""


class TrendSource(ABC):
    name: str = "base"

    @abstractmethod
    def fetch(self, niche: str = "", limit: int = 20) -> List[Trend]:
        """Trend olan konulari dondurur."""


class AnalyticsProvider(ABC):
    @abstractmethod
    def fetch_video_stats(self, video_id: str) -> dict:
        """Bir videonun performans metriklerini dondurur (CTR, AVD, retention...)."""
