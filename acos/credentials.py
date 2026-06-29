"""Kanal bazli kimlik bilgisi cozumleyici (env tabanli).

Once kanala ozel `ACOS_<KANAL>_<AD>`, yoksa global `<AD>` env'ine bakar.
Boylece her kanal kendi YouTube/TikTok/Instagram token'larini tasiyabilir.
"""
import os
import re


def _slug(channel: str) -> str:
    return re.sub(r"[^A-Z0-9]+", "_", (channel or "").upper()).strip("_")


def cred(name: str, channel: str = "", default: str = "") -> str:
    if channel:
        v = os.environ.get(f"ACOS_{_slug(channel)}_{name}")
        if v:
            return v
    return os.environ.get(name, default)


def require(name: str, channel: str = "") -> str:
    v = cred(name, channel)
    if not v:
        scope = f" (kanal: {channel})" if channel else ""
        raise KeyError(f"Eksik kimlik bilgisi: {name}{scope}")
    return v
