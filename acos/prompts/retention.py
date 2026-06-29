"""Retention-odakli prompt motoru.

Amac: ilk 2 saniye, hook, curiosity gap, pattern interrupt, acik donguler,
hikaye akisi, CTA ve loop etkisini maksimize eden senaryolar uretmek.

Promptlar koddan ayri tutulur ki analytics geri beslemesiyle (kazanan
desenler) zamanla otomatik gelistirilebilsin.
"""
import json
import re
from typing import List, Optional

from ..interfaces import ScriptPackage, Scene

SYSTEM = (
    "You are an elite short-form video scriptwriter behind multiple viral, "
    "high-retention faceless channels (YouTube Shorts, TikTok, Reels). "
    "You understand the psychology of watch-time: the first 2 seconds decide "
    "everything, curiosity gaps keep people watching, pattern interrupts reset "
    "attention, open loops must only close at the end, and a loop line at the "
    "end should connect back to the opening so the video replays seamlessly. "
    "You write tight, punchy, spoken-word narration with zero filler."
)

_SCHEMA = """Return ONLY raw JSON (no markdown, no code fences) with EXACTLY these keys:
{
  "title": "<=80 chars, curiosity-driven, no clickbait lies",
  "title_variants": ["2 alternative titles for A/B testing"],
  "hook": "the spoken first line (<=12 words) — a pattern interrupt or bold claim",
  "narration": "FULL voiceover, 110-150 words (~40-55s). MUST start with the hook. Use an open loop early ('but here's what nobody tells you...'), keep sentences short and spoken, build curiosity, then deliver payoff. End with the loop_line.",
  "loop_line": "final spoken line that loops back to the hook so the video replays seamlessly",
  "cta": "a soft, native call to action (e.g. 'follow for part 2')",
  "scenes": [
    {"narration": "sentence", "visual_keyword": "1-3 word ENGLISH stock search term", "on_screen_text": "short caption"}
  ],
  "keywords": ["4-6 simple ENGLISH stock-footage search terms, concrete and visual"],
  "description": "2 sentences + 3 relevant hashtags",
  "tags": ["8-12 short keyword strings"]
}"""


def build_user_prompt(topic: str, niche: str, language: str = "en",
                      trends: Optional[List[str]] = None,
                      insights: Optional[str] = None,
                      directives: Optional[dict] = None) -> str:
    parts = [
        f"Niche: {niche}.",
        f"Topic / angle: {topic}.",
        f"Narration language: {language} (write narration, hook, loop_line in this language; keep keywords in ENGLISH).",
    ]
    if trends:
        parts.append("Currently trending (use if it fits the niche, otherwise ignore): "
                     + "; ".join(trends[:8]))
    if insights:
        # Analytics geri beslemesi: kazanan desenleri taklit et.
        parts.append(insights)
    if directives:
        # A/B test motorundan gelen bu turun yonergeleri.
        if directives.get("target_words"):
            parts.append(f"Target narration length: about {directives['target_words']} words.")
        if directives.get("hook_style"):
            parts.append(f"Open with this style of hook: {directives['hook_style']}.")
    parts.append(_SCHEMA)
    return "\n\n".join(parts)


def parse_script(raw: str, voice: str, language: str = "en") -> ScriptPackage:
    """LLM ham ciktisini ScriptPackage'a cevirir (dayanikli JSON ayiklama)."""
    clean = raw.strip()
    clean = re.sub(r"^```(?:json)?|```$", "", clean, flags=re.M).strip()
    # Ilk { ... son } arasini al (model bazen aciklama ekler).
    m = re.search(r"\{.*\}", clean, re.S)
    data = json.loads(m.group(0) if m else clean)

    scenes = [Scene(narration=s.get("narration", ""),
                    visual_keyword=s.get("visual_keyword", ""),
                    on_screen_text=s.get("on_screen_text", ""))
              for s in data.get("scenes", []) if isinstance(s, dict)]

    keywords = data.get("keywords") or [s.visual_keyword for s in scenes if s.visual_keyword]
    keywords = [k for k in keywords if k][:6] or [data.get("title", "abstract")]

    return ScriptPackage(
        title=data.get("title", "").strip(),
        narration=data.get("narration", "").strip(),
        keywords=keywords,
        description=data.get("description", "").strip(),
        tags=[t for t in (data.get("tags") or []) if t][:15],
        hook=data.get("hook", "").strip(),
        cta=data.get("cta", "").strip(),
        loop_line=data.get("loop_line", "").strip(),
        title_variants=[t for t in (data.get("title_variants") or []) if t][:3],
        scenes=scenes,
        language=language,
        voice=voice,
    )
