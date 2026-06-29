"""Claude (Anthropic) LLM provider — senaryo/baslik/etiket uretimi.

Maliyet icin varsayilan model Haiku; istege gore degistirilebilir.
"""
import json
import os
import urllib.request

from ...errors import LLMError
from ...interfaces import LLMProvider
from ...logging_utils import get_logger
from ...retry import retry

log = get_logger("llm.anthropic")
API_URL = "https://api.anthropic.com/v1/messages"


class AnthropicProvider(LLMProvider):
    def __init__(self, model: str = "claude-haiku-4-5-20251001", api_key: str = ""):
        self.model = model
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        if not self.api_key:
            raise LLMError("ANTHROPIC_API_KEY tanimli degil")

    @retry(times=3, base_delay=2.0, exceptions=(urllib.error.URLError, LLMError))
    def generate(self, system: str, user: str, max_tokens: int = 1024) -> str:
        body = json.dumps({
            "model": self.model,
            "max_tokens": max_tokens,
            "system": system,
            "messages": [{"role": "user", "content": user}],
        }).encode("utf-8")
        req = urllib.request.Request(API_URL, data=body, headers={
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        })
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.load(resp)
        except urllib.error.HTTPError as exc:
            raise LLMError(f"Anthropic HTTP {exc.code}: {exc.read()[:300]!r}") from exc
        try:
            return data["content"][0]["text"]
        except (KeyError, IndexError) as exc:
            raise LLMError(f"Beklenmeyen yanit: {data}") from exc
