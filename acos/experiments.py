"""A/B test motoru — surekli (continuous) deney + multi-armed bandit.

Her uretimde, aktif deneylerin (voice, tempo, hook stili, altyazi yogunlugu...)
her biri icin bir 'kol' (arm) secer. Kazananlari, yayinlanan videolarin retention
metriklerinden ogrenir ve uretimi zamanla kazanan kollara kaydirir.

Odul metrigi onceligi: averageViewPercentage (retention) -> yoksa goruntulenme.
Strateji: epsilon-greedy + warmup (her kol once birkac kez denenir).
"""
import random
from typing import Dict, List, Tuple

from .config import ChannelConfig
from .logging_utils import get_logger
from .store import Store

log = get_logger("experiments")

EPSILON = 0.2     # kesif olasiligi
WARMUP = 3        # her kol en az bu kadar sonuc alana dek kesif

# Bu deneyler 'directive' olarak prompt'a/render'a uygulanir.
DIRECTIVE_DIMS = {"target_words", "hook_style"}
RENDER_DIMS = {"words_per_caption"}
VOICE_DIM = "voice"


def _reward(arm_stat: dict) -> float:
    pct = arm_stat.get("pct")
    return float(pct) if pct is not None else float(arm_stat.get("views") or 0.0)


def _select_arm(arms: List, rewards: Dict[str, dict]) -> str:
    """epsilon-greedy + warmup. Once az denenmis kollar, sonra en iyiyi somur."""
    arms = [str(a) for a in arms]
    under = [a for a in arms if rewards.get(a, {}).get("n_stats", 0) < WARMUP]
    if under:
        return random.choice(under)
    if random.random() < EPSILON:
        return random.choice(arms)
    return max(arms, key=lambda a: _reward(rewards.get(a, {})))


class ExperimentEngine:
    def __init__(self, store: Store):
        self.store = store

    # --------------------------------------------------------------- secim
    def select(self, cfg: ChannelConfig) -> Dict[str, str]:
        """Aktif her deney icin bir kol secer: {deney_adi: secilen_kol}."""
        choices: Dict[str, str] = {}
        for name, arms in (cfg.experiments or {}).items():
            if not arms:
                continue
            rewards = self.store.arm_rewards(cfg.name, name)
            choices[name] = _select_arm(arms, rewards)
        if choices:
            log.info("A/B secimleri: %s", choices)
        return choices

    # --------------------------------------------------------------- uygula
    @staticmethod
    def apply(choices: Dict[str, str], cfg: ChannelConfig) -> Tuple[str, dict]:
        """Secimleri uygular. (voice_override, prompt_directives) dondurur.
        words_per_caption gibi render boyutlarini cfg uzerinde gunceller.
        """
        voice = ""
        directives: dict = {}
        for dim, arm in choices.items():
            if dim == VOICE_DIM and arm:
                voice = arm
            elif dim in RENDER_DIMS:
                try:
                    setattr(cfg.render, dim, int(arm))
                except (ValueError, TypeError):
                    pass
            elif dim in DIRECTIVE_DIMS:
                directives[dim] = arm
        return voice, directives

    # --------------------------------------------------------------- kayit
    def record(self, video_pk: int, choices: Dict[str, str]) -> None:
        for name, arm in choices.items():
            self.store.record_assignment(video_pk, name, arm)

    # ------------------------------------------------------------ rapor
    def leaderboard(self, cfg: ChannelConfig) -> Dict[str, list]:
        board: Dict[str, list] = {}
        for name, arms in (cfg.experiments or {}).items():
            rewards = self.store.arm_rewards(cfg.name, name)
            rows = []
            for a in arms:
                st = rewards.get(str(a), {})
                rows.append({
                    "arm": str(a), "n": st.get("n_stats", 0),
                    "reward": round(_reward(st), 2) if st else 0.0,
                    "avg_view_pct": st.get("pct"), "avg_views": st.get("views"),
                })
            rows.sort(key=lambda r: r["reward"], reverse=True)
            board[name] = rows
        return board
