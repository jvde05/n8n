# YouTube Shorts Otomasyonu (n8n, self-host)

Faceless YouTube Shorts'u **otomatik** uretip yukleyen, mumkun oldugunca **ucretsiz**
ve **kendi sunucunda** calisan bir n8n kurulumu.

Akis (her calismada bir Short):

```
Zamanlayici → Kanal Ayarlari (konu sec) → Claude (senaryo/baslik/etiket)
   → Isi Hazirla → FFmpeg Render (TTS + stok video + altyazi) → YouTube'a Yukle
```

| Parca            | Araç                         | Ucret                          |
|------------------|------------------------------|--------------------------------|
| Orkestrasyon     | n8n (Docker)                 | Ucretsiz                       |
| Senaryo/baslik   | Claude Haiku API             | Cok ucuz (~Short basina sent altina) |
| Seslendirme      | edge-tts (Microsoft)         | **Ucretsiz**                   |
| Arka plan video  | Pexels API                   | **Ucretsiz**                   |
| Render           | FFmpeg (kendi sunucun)       | **Ucretsiz**                   |
| Yukleme          | YouTube Data API v3          | **Ucretsiz** (kota dahilinde)  |

---

## 1. Gereksinimler

- Docker + Docker Compose kurulu bir sunucu/PC
- API anahtarlari:
  - **Anthropic** (Claude): https://console.anthropic.com
  - **Pexels** (ucretsiz): https://www.pexels.com/api/
  - **Google Cloud** (YouTube yukleme icin OAuth) — asagida anlatiliyor

## 2. Kurulum

```bash
git clone <bu-repo>
cd n8n
cp .env.example .env
# .env dosyasini ac, ANTHROPIC_API_KEY ve PEXELS_API_KEY gir

mkdir -p data
# data klasorune n8n (uid 1000) yazabilmeli:
sudo chown -R 1000:1000 data

docker compose up -d --build
```

n8n: **http://localhost:5678** (ilk girişte kullanıcı oluştur).

> Sunucuda calistiriyorsan `.env` icinde `N8N_HOST`, `WEBHOOK_URL` ve
> `N8N_PROTOCOL` degerlerini kendi alan adina gore ayarla (HTTPS icin reverse
> proxy oner: Caddy/Nginx).

## 3. YouTube baglantisi (OAuth)

YouTube'a yukleme yapabilmek icin bir kez Google tarafinda OAuth kurman gerekir:

1. https://console.cloud.google.com → yeni proje
2. **APIs & Services → Library → YouTube Data API v3 → Enable**
3. **OAuth consent screen**: External, uygulamani olustur, **Test users**'a
   YouTube hesabinin e-postasini ekle (yayina almana gerek yok)
4. **Credentials → Create Credentials → OAuth client ID → Web application**
5. **Authorized redirect URI** olarak n8n'in verdigi adresi ekle:
   `http://localhost:5678/rest/oauth2-credential/callback`
   (sunucuda kendi alan adin)
6. Client ID + Client Secret'i kopyala
7. n8n'de: **Credentials → New → YouTube OAuth2 API** → ID/Secret yapistir →
   **Connect** → Google ile giris yap, izin ver

> **Cok kanal:** Her YouTube kanali icin ayri bir "YouTube OAuth2 API" kimlik
> bilgisi olustur (her birinde ilgili Google hesabiyla giris yap).

## 4. Workflow'u ice aktar

1. n8n → sag ust **⋯ → Import from File** → `workflows/youtube-shorts.json`
2. **YouTube'a Yukle** node'unu ac → ilgili kanalin **YouTube OAuth2** kimligini sec
3. Kaydet.

İlk test: workflow'u acip **Execute Workflow** ile manuel calistir. `data/jobs/<id>/`
altinda `output.mp4` olusmali ve YouTube'a **private** (gizli) olarak yuklenmeli.

## 5. Cok kanal (3-4 hesap) kurulumu

Her kanal = workflow'un bir kopyasi:

1. Workflow'u **Duplicate** et (ornek: "Shorts - Kanal 2")
2. **Kanal Ayarlari** node'unu ac, `channel` nesnesini degistir:
   - `name`: kanal adi
   - `voice`: ses (TR: `tr-TR-EmelNeural` / `tr-TR-AhmetNeural`, EN: `en-US-AriaNeural`)
   - `topics`: o kanalin konu listesi (sen belirliyorsun — buraya istedigin
     kadar konu yaz, her calismada rastgele biri secilir)
3. **YouTube'a Yukle** node'unda o kanalin **OAuth kimligini** sec
4. Her workflow'u aktif et.

## 6. Gunde 5-10 video

**Zamanlayici** node'undaki cron ifadesi gunluk uretim sayisini belirler.
Varsayilan: `0 8,11,14,17,20 * * *` → gunde **5** video (08, 11, 14, 17, 20).

Daha fazlasi icin saat ekle, ornek 10/gun:
```
0 8,10,12,14,16,18,20,21,22,23 * * *
```

> **Onemli:** YouTube yeni kanallarda gunluk yukleme limiti uygular
> (dogrulanmamis hesaplarda dusuk olabilir). Kanalini telefonla dogrula ve
> agresif baslama; gunde birkac videoyla baslayip artir. Spam/telifsiz
> icerikten kacin, aksi halde kanal kapatilabilir.

## 7. Yayina alma (private → public)

Varsayilan olarak videolar **private** yuklenir ki once kontrol edebilesin.
Her sey yolundaysa **YouTube'a Yukle** node → `options → privacyStatus` degerini
`public` yap.

## 8. Ozellestirme ipuclari

- **Arka plan muzigi:** `scripts/assets/bgm.mp3` koyarsan otomatik eklenir.
- **Altyazi stili:** `scripts/make_short.py` icindeki `style` satiri (font, boyut,
  renk, konum) degistirilebilir.
- **Video suresi/gorunum:** `make_short.py` basindaki `W,H,FPS` ve `normalize_clip`
  klip sureleri.
- **Senaryo dili/tonu:** **Claude - Senaryo Uret** node'undaki prompt'u degistir
  (orn. Turkce narration istersen prompt'a "narration in Turkish" ekle ve `voice`'u
  `tr-TR-...` yap).

## 9. Kalite / optimizasyon (YouTube re-encode'a karsi)

YouTube her videoyu yeniden sikistirir; amac ona **temiz, yuksek kaliteli** kaynak
vermek ki bozma minimum olsun. Render pipeline buna gore ayarli:

- **Tek nesil encode:** Klipler stream-copy ile birlestirilir (yeniden encode yok),
  sadece son adimda **bir kez** yuksek kaliteli encode yapilir. Boylece cok-nesilli
  kalite kaybi onlenir.
- **CRF 18 + preset slow + profile high** — gorsel kalite/dosya dengesi yuksek.
- **BT.709 renk + lanczos olceklendirme** — renk kaymasi ve bulaniklik onlenir.
- **48kHz / 256k AAC** ses.
- **Pexels'ten en yuksek cozunurluklu dikey klip** secilir (mumkunse upscale yok).

Daha da yukari cekmek istersen (`scripts/make_short.py`):
- **4K dikey:** `W, H = 2160, 3840`. YouTube >=1080p Shorts'a daha iyi codec
  (VP9/AV1) verir; 4K'da fark daha belirgin olur ama render ~3-4x yavaslar ve
  Pexels'te her konuda 4K dikey bulunmayabilir. **Oneri: 1080x1920'de kal**, kalite
  zaten yeterli ve uretim hizli.
- **Daha keskin:** `-crf 18` yerine `-crf 16` (dosya buyur, kalite artar).
- **Yuksek hareket** (oyun/aksiyon) icin `-preset slow` yerine `-preset slower`.

> Not: 60fps istersen `FPS = 60` yap **ve** Pexels'te 60fps klip sec; aksi halde
> 30fps kaynagi 60'a cikarmak kalite katmaz, sadece dosyayi buyutur.

## 10. Kendi PC'nde calistirma (sunucu gerekmez)

Bu sistem kendi bilgisayarinda sorunsuz calisir; **disariya port acmana, statik IP
veya alan adina gerek yoktur.**

**Baglantilar nasil isliyor:**
- **n8n arayuzu** sadece `localhost:5678`'de, kendi tarayicinda acilir (disa kapali).
- **Claude / Pexels / YouTube** cagrilari PC'den internete *cikan* (outbound)
  isteklerdir — her ev modeminin arkasinda calisir, modem ayari gerekmez.
- **YouTube OAuth:** redirect URI olarak `http://localhost:5678/rest/oauth2-credential/callback`
  yeterli. Baglanirken tarayici ayni PC'de oldugu icin Google `localhost`'a geri
  donebilir — public IP gerekmez.

> `.env` icindeki `N8N_HOST` / `WEBHOOK_URL` / `N8N_PROTOCOL` sadece **uzak sunucu**
> kurulumu icindir. Kendi PC'nde `localhost` olarak birak.

**Tek sart — PC acik olmali:** Zamanlayici tetiklendiginde PC acik ve Docker
calisiyor olmali. Uyku/kapali ise o video uretilmez.
- Windows: *Ayarlar → Guc → Uyku: Asla* (uretim saatlerinde).
- 7/24 istersen kodun aynisini ~5$/ay bir VPS'e veya hep-acik bir mini PC'ye tasi.

**Gereksinim:** Docker Desktop (Windows/Mac) veya Docker Engine (Linux). ~2-4 GB RAM.
Render CPU kullanir; normal bir PC'de video basina ~1-3 dk.

**Windows / Mac izin notu:** README adim 2'deki `sudo chown -R 1000:1000 data`
komutu **sadece Linux** icindir. Docker Desktop (Windows/Mac) dosya izinlerini
kendi yonettigi icin bu adimi **atla** — bind mount otomatik calisir. (Sorun
yasarsan compose'da `./data:/data` yerine adlandirilmis volume kullanabilirsin.)

## Sorun giderme

- **Render node hata veriyor:** `docker compose logs -f n8n` ile ffmpeg/edge-tts
  ciktisina bak. Cogu zaman Pexels anahtari eksik ya da disk izni (`data` chown).
- **`require is not defined` (Code node):** compose'daki
  `NODE_FUNCTION_ALLOW_BUILTIN=fs,...` env'inin gectiginden emin ol, container'i
  yeniden olustur (`docker compose up -d --build`).
- **`$env.ANTHROPIC_API_KEY` bos:** `.env`'i doldurup `docker compose up -d` ile
  yeniden baslat.
- **YouTube 401/403:** OAuth kimligini yeniden baglan; Google projesinde test
  user olarak ekli oldugundan emin ol.
