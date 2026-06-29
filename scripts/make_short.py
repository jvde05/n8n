#!/usr/bin/env python3
"""
Bir 'job' klasoru alir, icindeki job.json'a gore:
  1) edge-tts ile seslendirme (ucretsiz)
  2) Pexels'ten dikey stok video indirir (ucretsiz)
  3) ffmpeg ile 1080x1920 dikey Short uretir (yanan altyazi + opsiyonel muzik)
Cikti:  <job_dir>/output.mp4

Kullanim:  python3 make_short.py /data/jobs/<id>
job.json ornegi:
  { "title": "...", "narration": "...", "keywords": ["space","stars"], "voice": "en-US-AriaNeural" }
"""
import json, os, sys, subprocess, random, urllib.request, urllib.parse, re

W, H, FPS = 1080, 1920, 30
PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")
BGM = "/scripts/assets/bgm.mp3"   # varsa arka plan muzigi (opsiyonel)
FONT = "DejaVu Sans"


def run(cmd, check=True):
    print("+", " ".join(str(c) for c in cmd), flush=True)
    return subprocess.run(cmd, check=check)


def ffprobe_duration(path):
    out = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", path
    ])
    return float(out.strip())


def pexels_videos(keyword, want=2):
    """Verilen anahtar kelime icin dikey video URL'leri dondurur."""
    if not PEXELS_KEY:
        return []
    url = "https://api.pexels.com/videos/search?" + urllib.parse.urlencode({
        "query": keyword, "orientation": "portrait", "size": "large", "per_page": 12
    })
    req = urllib.request.Request(url, headers={"Authorization": PEXELS_KEY})
    try:
        data = json.load(urllib.request.urlopen(req, timeout=30))
    except Exception as e:
        print("Pexels hata:", e, flush=True)
        return []
    results = []
    for v in data.get("videos", []):
        files = [f for f in v.get("video_files", []) if (f.get("height") or 0) >= (f.get("width") or 0)]
        # En az hedef genislikte olanlari tercih et (upscale yok), yoksa en buyugu.
        hd = [f for f in files if (f.get("width") or 0) >= W]
        pool = hd or files
        pool.sort(key=lambda f: (f.get("width") or 0) * (f.get("height") or 0), reverse=True)
        if pool:
            results.append(pool[0]["link"])
        if len(results) >= want:
            break
    return results


def download(url, dest):
    try:
        urllib.request.urlretrieve(url, dest)
        return os.path.getsize(dest) > 1000
    except Exception as e:
        print("Indirme hata:", e, flush=True)
        return False


def normalize_clip(src, dst, seconds=6):
    """Klibi 1080x1920'ye crop/scale eder, sessiz ve sabit fps yapar."""
    # Yuksek kaliteli ara dosya (CRF 16). Lanczos olceklendirme keskinligi korur.
    vf = (f"scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,"
          f"crop={W}:{H},fps={FPS},setsar=1,format=yuv420p")
    run(["ffmpeg", "-y", "-t", str(seconds), "-i", src, "-an",
         "-vf", vf, "-c:v", "libx264", "-preset", "fast", "-crf", "16",
         "-profile:v", "high", "-pix_fmt", "yuv420p",
         "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
         dst])


def color_bg(dst, seconds):
    """Stok bulunamazsa duz gradient arka plan."""
    run(["ffmpeg", "-y", "-f", "lavfi",
         "-i", f"color=c=0x101820:s={W}x{H}:d={seconds}:r={FPS}",
         "-vf", "noise=alls=8:allf=t,format=yuv420p", "-c:v", "libx264",
         "-crf", "18", "-pix_fmt", "yuv420p", dst])


def vtt_to_srt(vtt_path, srt_path, words_per_line=4):
    """edge-tts kelime bazli VTT'sini gruplayip okunabilir SRT'ye cevirir."""
    if not os.path.exists(vtt_path):
        return False
    txt = open(vtt_path, encoding="utf-8").read()
    cues = re.findall(
        r"(\d\d:\d\d:\d\d[.,]\d+)\s*-->\s*(\d\d:\d\d:\d\d[.,]\d+)\s*\n(.+?)(?=\n\n|\Z)",
        txt, re.S)
    if not cues:
        return False
    words = [(s.replace(".", ","), e.replace(".", ","), t.strip().replace("\n", " "))
             for s, e, t in cues]
    lines = []
    for i in range(0, len(words), words_per_line):
        grp = words[i:i + words_per_line]
        lines.append((grp[0][0], grp[-1][1], " ".join(w[2] for w in grp)))
    with open(srt_path, "w", encoding="utf-8") as f:
        for i, (s, e, t) in enumerate(lines, 1):
            f.write(f"{i}\n{s} --> {e}\n{t}\n\n")
    return True


def main():
    job_dir = sys.argv[1]
    job = json.load(open(os.path.join(job_dir, "job.json"), encoding="utf-8"))
    narration = (job.get("narration") or job.get("title") or "").strip()
    keywords = job.get("keywords") or [job.get("title", "nature")]
    voice = job.get("voice") or os.environ.get("TTS_VOICE", "en-US-AriaNeural")

    voice_mp3 = os.path.join(job_dir, "voice.mp3")
    vtt = os.path.join(job_dir, "subs.vtt")
    srt = os.path.join(job_dir, "subs.srt")
    out = os.path.join(job_dir, "output.mp4")

    # 1) Seslendirme (ucretsiz)
    run(["edge-tts", "--voice", voice, "--text", narration,
         "--write-media", voice_mp3, "--write-subtitles", vtt])
    dur = ffprobe_duration(voice_mp3) + 0.4
    has_subs = vtt_to_srt(vtt, srt)

    # 2) Stok video indir + normalize et
    clips = []
    for kw in keywords:
        for i, url in enumerate(pexels_videos(kw, want=2)):
            raw = os.path.join(job_dir, f"raw_{len(clips)}.mp4")
            if download(url, raw):
                norm = os.path.join(job_dir, f"clip_{len(clips)}.mp4")
                try:
                    normalize_clip(raw, norm)
                    clips.append(norm)
                except subprocess.CalledProcessError:
                    pass
        if len(clips) >= 6:
            break

    # 3) Arka plani sese gore uzunlukta birlestir
    bg = os.path.join(job_dir, "bg.mp4")
    if clips:
        seq, total, idx = [], 0.0, 0
        while total < dur:
            c = clips[idx % len(clips)]
            seq.append(c)
            total += ffprobe_duration(c)
            idx += 1
        concat_txt = os.path.join(job_dir, "concat.txt")
        with open(concat_txt, "w") as f:
            for c in seq:
                f.write(f"file '{c}'\n")
        # Klipler ayni codec/cozunurluk/fps oldugundan yeniden encode etmeden
        # birlestir (stream copy) -> bir nesil kalite kaybi onlenir.
        run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_txt,
             "-c", "copy", bg])
    else:
        color_bg(bg, dur)

    # 4) Altyazi + ses + (opsiyonel) muzik mix -> output.mp4
    style = (f"FontName={FONT},FontSize=16,PrimaryColour=&H00FFFFFF,"
             f"OutlineColour=&H00000000,BorderStyle=1,Outline=2,Shadow=1,"
             f"Alignment=2,MarginV=120,Bold=1")
    sub_filter = f"subtitles={srt}:force_style='{style}'" if has_subs else "null"

    cmd = ["ffmpeg", "-y", "-i", bg, "-i", voice_mp3]
    if os.path.exists(BGM):
        cmd += ["-stream_loop", "-1", "-i", BGM]
        fc = (f"[0:v]{sub_filter}[v];"
              f"[1:a]volume=2.0[a1];[2:a]volume=0.12[a2];"
              f"[a1][a2]amix=inputs=2:duration=first:dropout_transition=0[a]")
    else:
        fc = f"[0:v]{sub_filter}[v];[1:a]volume=2.0[a]"
    cmd += ["-filter_complex", fc, "-map", "[v]", "-map", "[a]",
            "-t", str(dur), "-r", str(FPS),
            # Tek ve son encode: yuksek kalite (CRF 18) + YouTube'un sevdigi profil/renk.
            "-c:v", "libx264", "-preset", "slow", "-crf", "18",
            "-profile:v", "high", "-level", "4.2", "-pix_fmt", "yuv420p",
            "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
            "-c:a", "aac", "-b:a", "256k", "-ar", "48000",
            "-movflags", "+faststart", out]
    run(cmd)

    print("OK:", out, flush=True)


if __name__ == "__main__":
    main()
