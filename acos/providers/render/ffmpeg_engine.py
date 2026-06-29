"""FFmpeg render motoru.

Tasarim ilkeleri:
- Tek nesil encode: klipler normalize edilir, stream-copy ile birlestirilir,
  yalnizca son adimda bir kez yuksek kaliteli encode yapilir.
- Cesitlilik: her klibe donusumlu dinamik zoom (Ken Burns) uygulanir; videolar
  birbirinin ayni gorunmez.
- Dayaniklilik: bir filtre/klip patlarsa daha basit yola duser, hic uretmemekten
  iyidir.
"""
import os
from typing import List

from ...config import RenderOptions
from ...errors import RenderError
from ...ffmpeg_utils import probe_duration, run
from ...interfaces import RenderEngine, TTSResult
from ...logging_utils import get_logger

log = get_logger("render.ffmpeg")

# Donusumlu hareket stilleri (zoompan zoom ifadesi) — cesitlilik icin.
_MOTIONS = [
    "min(1.0+0.0012*on,1.18)",   # yavas zoom-in
    "max(1.18-0.0012*on,1.0)",   # yavas zoom-out
]


class FFmpegRenderEngine(RenderEngine):
    def __init__(self, options: RenderOptions = None):
        self.o = options or RenderOptions()

    # ----------------------------------------------------------------- public
    def assemble(self, workdir: str, tts: TTSResult,
                 raw_clips: List[str], job: dict) -> str:
        o = self.o
        out = os.path.join(workdir, "output.mp4")
        dur = tts.duration

        norm_clips = self._normalize_all(raw_clips, workdir)
        bg = os.path.join(workdir, "bg.mp4")
        if norm_clips:
            self._concat(norm_clips, dur, bg, workdir)
        else:
            self._color_bg(bg, dur)

        self._finalize(bg, tts, dur, out)
        log.info("Render tamam: %s", out)
        return out

    # ------------------------------------------------------------- normalize
    def _normalize_all(self, raw_clips: List[str], workdir: str) -> List[str]:
        norm = []
        for i, src in enumerate(raw_clips):
            dst = os.path.join(workdir, f"clip_{i}.mp4")
            try:
                self._normalize(src, dst, motion_idx=i)
                norm.append(dst)
            except RenderError as exc:
                log.warning("Klip %d normalize edilemedi, atlandi: %s", i, exc)
        return norm

    def _normalize(self, src: str, dst: str, motion_idx: int) -> None:
        o = self.o
        base = (f"scale={o.width}:{o.height}:force_original_aspect_ratio=increase:"
                f"flags=lanczos,crop={o.width}:{o.height},fps={o.fps},setsar=1")
        common = ["-c:v", "libx264", "-preset", "fast", "-crf", "16",
                  "-profile:v", "high", "-pix_fmt", "yuv420p",
                  "-colorspace", "bt709", "-color_primaries", "bt709",
                  "-color_trc", "bt709", dst]
        if o.motion:
            z = _MOTIONS[motion_idx % len(_MOTIONS)]
            vf = (f"{base},zoompan=z='{z}':x='iw/2-(iw/zoom/2)':"
                  f"y='ih/2-(ih/zoom/2)':d=1:s={o.width}x{o.height}:fps={o.fps},"
                  f"format=yuv420p")
            try:
                run(["ffmpeg", "-y", "-t", str(o.clip_seconds), "-i", src,
                     "-an", "-vf", vf] + common)
                return
            except RenderError:
                log.warning("Hareketli render basarisiz, duz moda dusuluyor")
        # Fallback: hareketsiz
        run(["ffmpeg", "-y", "-t", str(o.clip_seconds), "-i", src,
             "-an", "-vf", base + ",format=yuv420p"] + common)

    # ---------------------------------------------------------------- concat
    def _concat(self, clips: List[str], dur: float, bg: str, workdir: str) -> None:
        seq, total, idx = [], 0.0, 0
        while total < dur and clips:
            c = clips[idx % len(clips)]
            seq.append(c)
            total += probe_duration(c)
            idx += 1
            if idx > 200:
                break
        listfile = os.path.join(workdir, "concat.txt")
        with open(listfile, "w") as f:
            for c in seq:
                f.write(f"file '{c}'\n")
        # Ayni codec/cozunurluk -> yeniden encode etmeden birlestir.
        run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", listfile,
             "-c", "copy", bg])

    def _color_bg(self, bg: str, dur: float) -> None:
        o = self.o
        run(["ffmpeg", "-y", "-f", "lavfi",
             "-i", f"color=c=0x101820:s={o.width}x{o.height}:d={dur}:r={o.fps}",
             "-vf", "noise=alls=8:allf=t,format=yuv420p",
             "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", bg])

    # -------------------------------------------------------------- finalize
    def _finalize(self, bg: str, tts: TTSResult, dur: float, out: str) -> None:
        o = self.o
        # Gorsel zinciri: sinematik renk + keskinlik + yanan altyazi.
        vchain = []
        if o.cinematic:
            vchain.append("eq=contrast=1.06:saturation=1.12:brightness=0.01")
            vchain.append("unsharp=5:5:0.3")
        if tts.subtitle_path:
            style = (f"FontName={o.font},FontSize=16,PrimaryColour=&H00FFFFFF,"
                     f"OutlineColour=&H00101010,BorderStyle=1,Outline=3,Shadow=1,"
                     f"Alignment=2,MarginV=170,Bold=1")
            vchain.append(f"subtitles={tts.subtitle_path}:force_style='{style}'")
        vfilter = "[0:v]" + (",".join(vchain) if vchain else "null") + "[v]"

        # Ses zinciri: seslendirme normalize (-14 LUFS) + opsiyonel muzik.
        voice_af = "loudnorm=I=-14:TP=-1.5:LRA=11" if o.loudnorm else "volume=2.0"
        cmd = ["ffmpeg", "-y", "-i", bg, "-i", tts.audio_path]
        has_bgm = os.path.exists(o.bgm_path)
        if has_bgm:
            cmd += ["-stream_loop", "-1", "-i", o.bgm_path]
            afilter = (f"[1:a]{voice_af}[a1];[2:a]volume={o.bgm_volume}[a2];"
                       f"[a1][a2]amix=inputs=2:duration=first:dropout_transition=0[a]")
        else:
            afilter = f"[1:a]{voice_af}[a]"

        cmd += ["-filter_complex", f"{vfilter};{afilter}",
                "-map", "[v]", "-map", "[a]", "-t", str(dur), "-r", str(o.fps),
                "-c:v", "libx264", "-preset", o.preset, "-crf", str(o.crf),
                "-profile:v", "high", "-level", "4.2", "-pix_fmt", "yuv420p",
                "-colorspace", "bt709", "-color_primaries", "bt709",
                "-color_trc", "bt709", "-c:a", "aac", "-b:a", "256k", "-ar", "48000",
                "-movflags", "+faststart", out]
        run(cmd)
