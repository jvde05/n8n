# Canli Kurulum & Ilk Test (uctan uca kanit)

Amac: sistemi kendi PC'nde bir kez **gercekten** uctan uca calistirip kanitlamak.
Asamali gidiyoruz — en riskli kisim (render) en basta, ucretsiz, YouTube gerekmeden.

> Ozet komut mantigi: her sey container icinde calisir, bu yuzden komutlar
> `docker compose exec n8n ...` ile verilir.

---

## 0. Gerekenler

- **Docker Desktop** (Windows/Mac) veya Docker Engine (Linux)
- **Anthropic API key** — https://console.anthropic.com (senaryo; cok ucuz)
- **Pexels API key** — https://www.pexels.com/api/ (stok video; **ucretsiz**)
- YouTube yuklemesi icin (Asama 2) Google OAuth — o bolumde anlatiliyor

## 1. Repoyu cek ve anahtarlari gir

```bash
git clone https://github.com/jvde05/n8n.git
cd n8n
cp .env.example .env
# .env ac: ANTHROPIC_API_KEY ve PEXELS_API_KEY doldur (Asama 1 icin bu ikisi yeter)
```

Linux'taysan veri klasorune yazma izni ver (Windows/Mac'te bu adimi ATLA):

```bash
mkdir -p data && sudo chown -R 1000:1000 data
```

## 2. Imaji kur ve baslat

```bash
docker compose up -d --build
docker compose logs -f n8n   # "Editor is now accessible" gorunce Ctrl+C
```

n8n arayuzu: http://localhost:5678 (ilk girişte kullanıcı oluştur).

---

## ASAMA 1 — Render testi (YouTube YOK, en kritik kanit)

Bu adim Claude senaryo + edge-tts seslendirme + Pexels stok video + FFmpeg
render zincirinin tamamini test eder. Sadece Anthropic + Pexels anahtari ister.

```bash
docker compose exec n8n python3 -m acos.cli run --channel /channels/example.yaml
```

Beklenen: loglar akar (seslendirme, klip indirme, render) ve sonunda bir JSON
basar (`output` = video yolu). Cikti dosyasi:

```
data/jobs/<is_id>/output.mp4
```

Bu dosyayi ac ve kontrol et:
- 1080x1920 dikey mi?
- Seslendirme + yanan altyazi + arka plan video var mi?
- Hareket (zoom) ve ses seviyesi normal mi?

> **Bu calistiysa projenin en zor parcasi kanitlanmis demektir.** 🎉
> Begenmedigin yerleri (altyazi boyutu, zoom, renk) `channels/example.yaml`
> > `render:` altindan veya `acos/providers/render/ffmpeg_engine.py`'den ayarlariz.

### Alternatif: n8n arayuzunden gorsel test
1. n8n > sag ust **⋯ > Import from File** > `workflows/youtube-shorts.json`
2. **Claude** node'una git, ANTHROPIC anahtarini gir (veya $env kullan).
3. **Execute Workflow** > `data/jobs/<id>/output.mp4` olusmali.

---

## ASAMA 2 — YouTube'a yukleme

Iki yol var. **Yol A** en kolayi (n8n OAuth ekranini halleder).
**Yol B** ACOS'un native (n8n'siz) yoludur ve 3-4 kanali script'le yonetmek icin daha guclu.

### Yol A — n8n YouTube node (kolay)
README'deki **"3. YouTube baglantisi (OAuth)"** ve **"4. Workflow'u ice aktar"**
adimlarini izle. n8n workflow'u render edip otomatik yukler.

### Yol B — ACOS native (refresh token ile)
1. https://console.cloud.google.com > proje olustur
2. **YouTube Data API v3**'u Enable et
3. **OAuth consent screen**: External, kendini **Test user** olarak ekle
4. **Credentials > OAuth client ID > Web application**; **Authorized redirect URIs**'e
   sunu ekle: `https://developers.google.com/oauthplayground`
5. **Refresh token al:** https://developers.google.com/oauthplayground
   - Sag ustteki diste (⚙) > **Use your own OAuth credentials** > Client ID/Secret yapistir
   - Sol listede su scope'lari sec:
     - `https://www.googleapis.com/auth/youtube.upload`
     - `https://www.googleapis.com/auth/youtube.readonly`
     - `https://www.googleapis.com/auth/yt-analytics.readonly`
   - **Authorize APIs** > Google ile giris > **Exchange authorization code for tokens**
   - **Refresh token**'i kopyala
6. `.env`'e yaz (sonra `docker compose up -d` ile yeniden baslat):
   ```
   YT_CLIENT_ID=...
   YT_CLIENT_SECRET=...
   YT_REFRESH_TOKEN=...
   ```
   > Birden cok kanal icin kanal-bazli: `ACOS_<KANAL_ADI>_YT_REFRESH_TOKEN=...`
   > (kanal adindaki bosluk/harf disi karakterler `_` olur, ornek kanal "Mind Blown Facts"
   > -> `ACOS_MIND_BLOWN_FACTS_YT_REFRESH_TOKEN`)
7. Uretip yukle (varsayilan **private** — once sen kontrol edersin):
   ```bash
   docker compose exec n8n python3 -m acos.cli run --channel /channels/example.yaml --publish
   ```
   Cikti JSON'unda `publish` altinda YouTube `video_id` ve `url` gorunur.
   YouTube Studio > Content'te video **private** olarak durur.

---

## ASAMA 3 — Ogrenme dongusu (birkac video + zaman sonra)

Videolar yayinlanip biraz veri biriktikten sonra:

```bash
# 1) Guncel metrikleri cek (views/likes/comments + yetki varsa retention)
docker compose exec n8n python3 -m acos.cli sync-stats --channel /channels/example.yaml

# 2) Kazanan desenleri cikar (prompt'a otomatik enjekte edilir)
docker compose exec n8n python3 -m acos.cli learn --channel /channels/example.yaml

# 3) A/B kollarinin skor tablosu
docker compose exec n8n python3 -m acos.cli experiments --channel /channels/example.yaml
```

Bundan sonra her yeni `run`, ogrenilen dersleri ve kazanan A/B kollarini kullanir.

---

## Trend kesfi (opsiyonel, anahtarsiz)

```bash
docker compose exec n8n python3 -m acos.cli discover --channel /channels/example.yaml
# Trend bir konuyla uretmek icin:
docker compose exec n8n python3 -m acos.cli run --channel /channels/example.yaml --use-trends
```

---

## Cok kanal (3-4 hesap)

1. `channels/example.yaml`'i kopyala: `channels/kanal2.yaml` vb.
2. Her birinde `name`, `niche`, `voice`, `topics`, `experiments` ve (Yol B icin)
   kanal-bazli `ACOS_<KANAL>_YT_REFRESH_TOKEN` ayarla.
3. Her kanali ayri `run` ile (veya n8n'de zamanlanmis ayri workflow ile) calistir.

---

## Sorun giderme

| Belirti | Cozum |
|--------|-------|
| `ANTHROPIC_API_KEY tanimli degil` | `.env` doldur, `docker compose up -d` ile yeniden baslat |
| Pexels atlandi / duz arka plan | `PEXELS_API_KEY` eksik veya gecersiz |
| Render hatasi | `docker compose logs -f n8n` ile ffmpeg ciktisina bak; cogu zaman izin (`data` chown) |
| `Permission denied` /data | Linux: `sudo chown -R 1000:1000 data` |
| YouTube 401/403 | refresh token/scopes'u kontrol et; Google projesinde test user olarak ekli misin? |
| Instagram `skipped` | IG public video URL ister (`job['hosted_url']`); su an yol haritasinda |

Takildigin yerde `docker compose logs -f n8n` ciktisini paylas — birlikte cozeriz.
