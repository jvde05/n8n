# ACOS — AI Content Operating System (Mimari)

> Bu repo artik sadece "YouTube Shorts ureten bir n8n akisi" degil; **moduler,
> platform-bagimsiz bir icerik uretim isletim sistemi**. Bugun YouTube Shorts,
> yarin TikTok / Reels / Pinterest / X — ayni cekirdek, farkli publisher.

## Katmanlar

```
                 ┌──────────────────────────────────────────┐
   Tetikleyici → │  n8n (ops/zamanlama/OAuth)  veya  ACOS CLI │
                 └───────────────────┬──────────────────────┘
                                     │
                         ┌───────────▼───────────┐
                         │   acos.pipeline        │  orkestrasyon
                         └───────────┬───────────┘
        ┌──────────────┬────────────┼────────────┬──────────────┐
        ▼              ▼            ▼            ▼              ▼
   TrendSource    LLMProvider   TTSProvider  VideoProvider  RenderEngine  Publisher
   (RSS:Google/   (Anthropic)   (edge-tts)   (Pexels)       (FFmpeg)      (n8n/native)
    Reddit)
```

Her kutu bir **arayuz** (bkz. `acos/interfaces.py`). Somut uygulamalar
`acos/providers/...` altinda. Config (`channels/*.yaml`) hangi uygulamanin
kullanilacagini secer. **Bir bileseni degistirmek pipeline'i degistirmez.**

## Dizin yapisi

```
acos/
  interfaces.py          # ABC sozlesmeleri + veri modelleri (ScriptPackage, Trend, ...)
  config.py              # ChannelConfig / RenderOptions (YAML/JSON)
  registry.py            # isim -> somut provider fabrikasi
  pipeline.py            # produce_video() ve run_job() orkestrasyonu
  prompts/retention.py   # retention-odakli prompt motoru + JSON ayiklama
  retry.py, logging_utils.py, errors.py, ffmpeg_utils.py
  providers/
    llm/anthropic_provider.py
    tts/edge_provider.py
    video/pexels_provider.py
    render/ffmpeg_engine.py
    publish/publishers.py   # Noop (n8n yukler) + youtube/tiktok/instagram (yol haritasi)
    trends/rss_sources.py   # Google Trends + Reddit (anahtarsiz, ucretsiz)
scripts/make_short.py    # n8n koprusu (job.json -> output.mp4)
channels/example.yaml    # kanal yapilandirma ornegi
workflows/               # n8n akislari
```

## Iki calisma modu

1. **n8n (varsayilan):** n8n senaryoyu uretir (Claude HTTP node), `make_short.py`
   ile ACOS render cekirdegini cagirir, YouTube node ile yukler. OAuth/kimlik
   yonetimi n8n'de — kolay.
2. **Standalone CLI:** `python -m acos.cli run --channel channels/x.yaml`
   — n8n olmadan uctan uca uretim (LLM -> render). Platform bagimsizligi icin.

```bash
python -m acos.cli discover --channel channels/example.yaml   # trend kesfi
python -m acos.cli run --channel channels/example.yaml --use-trends
python -m acos.cli render /data/jobs/<id>                      # n8n koprusu
```

---

## Yol haritasi (CTO onceligi)

**Faz 0–1 — TAMAMLANDI (bu surum):**
- [x] Monolitten moduler provider mimarisine gecis
- [x] retry + structured logging + hata hiyerarsisi
- [x] Retention-odakli prompt motoru (hook / curiosity gap / open loop / loop line)
- [x] Trend kesfi (Google Trends + Reddit, anahtarsiz)
- [x] FFmpeg upgrade: dinamik zoom (Ken Burns), sinematik renk, ses normalizasyonu
- [x] Config-driven kanallar (YAML), CLI

**Faz 2 — Cok platform yayini — TAMAMLANDI:**
- [x] Native YouTube Data API uploader (refresh-token, n8n bagimsiz)
- [x] TikTok Content Posting API + Instagram Graph API publisher'lari
- [x] Platform basina format profilleri + metadata/hashtag uretimi (`platforms.py`)
- [x] `publish_all`: tek render -> tum platformlar (biri patlarsa digerleri devam)

**Faz 3 — Analytics geri besleme dongusu (self-learning) — TAMAMLANDI:**
- [x] AnalyticsProvider: views/likes/comments + (yetki varsa) AVD/izlenme yuzdesi
- [x] Performans veritabani (SQLite, `store.py`)
- [x] Kazanan desen cikarimi (`learning.py`) + prompt'a otomatik enjeksiyon
- [x] CLI: `sync-stats` (metrik cek) ve `learn` (insights uret)

> Akis: yayinla -> `sync-stats` (metrikleri topla) -> `learn` (kazanan
> desenleri cikar) -> bir sonraki `run` bu insights'i prompt'a enjekte eder.
> Sistem boylece kendi en iyi videolarini taklit etmeyi ogrenir.

**Faz 4 — A/B test motoru — TAMAMLANDI:**
- [x] Surekli deney cercevesi (`experiments.py`): voice / tempo / hook stili /
      altyazi yogunlugu kollari config'ten tanimlanir
- [x] Cok kollu haydut (epsilon-greedy + warmup) ile kol secimi
- [x] Atamalar SQLite'ta (`assignments`); odul = retention (avg_view_pct) -> yoksa views
- [x] Pipeline entegrasyonu: sec -> uygula (prompt/render/voice) -> yayinla -> youtube'a bagla
- [x] CLI: `experiments` (kol bazli skor tablosu)

> Akis: `run` her turda bir kol secer ve uygular; `sync-stats` metrikleri ceker;
> motor kazanan kollari ogrenip uretimi onlara kaydirir. Tamamen otomatik.

**Faz 5 — Maliyet & olcek:**
- [ ] LLM yanit cache + prompt kisaltma + model kademeleme
- [ ] Render kuyrugu/worker'lar, idempotent isler, gozlemlenebilirlik

**Faz 6 — Gelismis render:**
- [ ] Karaoke/animasyonlu altyazilar, emoji, motion graphics, akici gecisler (xfade)
