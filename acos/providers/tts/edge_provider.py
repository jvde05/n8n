"""edge-tts (Microsoft) seslendirme provider'i — ucretsiz, cok dilli.

Kelime zamanlamalarini okunabilir altyaziya (SRT) gruplar.
"""
import os
import re
import subprocess

from ...errors import TTSError
from ...ffmpeg_utils import probe_duration
from ...interfaces import TTSProvider, TTSResult
from ...logging_utils import get_logger
from ...retry import retry

log = get_logger("tts.edge")


class EdgeTTSProvider(TTSProvider):
    def __init__(self, words_per_caption: int = 3):
        self.words_per_caption = words_per_caption

    @retry(times=2, base_delay=2.0, exceptions=(subprocess.CalledProcessError,))
    def synthesize(self, text: str, voice: str, workdir: str) -> TTSResult:
        audio = os.path.join(workdir, "voice.mp3")
        vtt = os.path.join(workdir, "subs.vtt")
        srt = os.path.join(workdir, "subs.srt")
        proc = subprocess.run(
            ["edge-tts", "--voice", voice, "--text", text,
             "--write-media", audio, "--write-subtitles", vtt],
            capture_output=True, text=True,
        )
        if proc.returncode != 0 or not os.path.exists(audio):
            raise TTSError(f"edge-tts hatasi: {proc.stderr[-400:]}")
        dur = probe_duration(audio) + 0.4
        sub = srt if self._vtt_to_srt(vtt, srt) else None
        log.info("Seslendirme hazir (%.1fs, ses=%s)", dur, voice)
        return TTSResult(audio_path=audio, subtitle_path=sub, duration=dur)

    def _vtt_to_srt(self, vtt_path: str, srt_path: str) -> bool:
        if not os.path.exists(vtt_path):
            return False
        txt = open(vtt_path, encoding="utf-8").read()
        cues = re.findall(
            r"(\d\d:\d\d:\d\d[.,]\d+)\s*-->\s*(\d\d:\d\d:\d\d[.,]\d+)\s*\n(.+?)(?=\n\n|\Z)",
            txt, re.S)
        if not cues:
            return False
        words = [(s.replace(".", ","), e.replace(".", ","),
                  t.strip().replace("\n", " ")) for s, e, t in cues]
        n = max(1, self.words_per_caption)
        with open(srt_path, "w", encoding="utf-8") as f:
            for i in range(0, len(words), n):
                grp = words[i:i + n]
                idx = i // n + 1
                f.write(f"{idx}\n{grp[0][0]} --> {grp[-1][1]}\n"
                        f"{' '.join(w[2] for w in grp)}\n\n")
        return True
