# Çözüm Oto Elektrik — Renault Elektronik Servisi

Renault EDC şanzıman, mekatronik beyin onarımı ve oto elektronik servisi için
**PHP Slim 4** ile geliştirilmiş kurumsal web sitesi ve yönetim paneli.

Eski statik/CMS site, veritabanı destekli, yönetilebilir ve SEO odaklı modern bir
yapıya taşınmıştır. Hizmet × İlçe landing sayfaları **dinamik** olarak üretilir:
panelden bir hizmet veya ilçe eklediğinizde ilgili SEO sayfaları otomatik oluşur.

## Özellikler

- **Slim 4 + Twig + PHP-DI** tabanlı temiz mimari (PSR-4, repository deseni)
- **Yönetim paneli** (`/yonetim`): hizmetler, ilçeler, sayfalar, S.S.S., galeri,
  iletişim mesajları, site ayarları ve şifre yönetimi
- **Dinamik SEO landing sayfaları**: 10 hizmet × 18 ilçe = otomatik 180+ sayfa
- **Dinamik `sitemap.xml` ve `robots.txt`**
- **Eski URL'ler için 301 yönlendirme** (`/icerik/...` → yeni temiz URL'ler)
- **İletişim formu** (CSRF korumalı, spam bal küpü) → panelde mesaj yönetimi
- **Galeri** görsel yükleme (JPG/PNG/WEBP/GIF)
- MySQL (production) ve SQLite (lokal geliştirme) desteği
- Mobil uyumlu, modern otomotiv temalı tasarım
- Güvenlik: CSRF, oturum, parola hash (`password_hash`), `noindex` panel

## Teknoloji

| Katman      | Kullanılan                          |
|-------------|-------------------------------------|
| Dil         | PHP 8.1+                            |
| Framework   | Slim 4                              |
| Şablon      | Twig 3                             |
| DI          | PHP-DI 7                           |
| Veritabanı  | MySQL 5.7+/MariaDB veya SQLite 3   |
| Bağımlılık  | Composer                           |

## Kurulum (Lokal Geliştirme — SQLite)

```bash
composer install
cp .env.example .env
# .env içinde DB_DRIVER=sqlite yapın (lokal için)
php database/migrate.php   # şemayı kurar
php database/seed.php      # başlangıç verilerini yükler
composer start             # http://localhost:8080
```

- Site: <http://localhost:8080>
- Panel: <http://localhost:8080/yonetim/giris>
  (varsayılan: `.env` içindeki `ADMIN_EMAIL` / `ADMIN_PASSWORD`)

## Production Kurulumu (Paylaşımlı Hosting / MySQL)

1. **Dosyaları yükleyin** ve `composer install --no-dev --optimize-autoloader` çalıştırın.
2. **Web kök dizinini `public/` klasörüne** yönlendirin (alan adı document root = `public`).
   Bu mümkün değilse, hosting kök dizinindeki `.htaccess` ile `public/`'e yönlendirin.
3. **`.env` oluşturun** (`.env.example`'ı kopyalayıp düzenleyin):
   ```
   APP_ENV=production
   APP_DEBUG=false
   APP_URL=https://www.renaultelektronikservisi.com.tr
   DB_DRIVER=mysql
   DB_HOST=localhost
   DB_NAME=...
   DB_USER=...
   DB_PASS=...
   ADMIN_EMAIL=...
   ADMIN_PASSWORD=...   # güçlü bir parola
   ```
4. **Şema + veri:**
   ```bash
   php database/migrate.php
   php database/seed.php
   ```
5. **İlk girişten sonra** panelden (`/yonetim/hesap`) şifrenizi değiştirin.
6. `public/assets/uploads/` klasörünün **yazılabilir** (755/775) olduğundan emin olun.

> Apache için `public/.htaccess` hazırdır. Nginx kullanıyorsanız tüm istekleri
> `public/index.php`'ye yönlendirin (`try_files $uri /index.php$is_args$args;`).

## Yönetim Paneli

| Bölüm        | Açıklama                                                        |
|--------------|----------------------------------------------------------------|
| Panel        | Özet istatistikler ve son mesajlar                            |
| Hizmetler    | Hizmet ekle/düzenle/sil; ilçe sayfası üretimini aç/kapat      |
| İlçeler      | İlçe ekle/düzenle/sil; aktif ilçeler otomatik landing üretir  |
| Sayfalar     | Hakkımızda vb. serbest sayfalar                               |
| S.S.S.       | Genel veya hizmete özel sıkça sorulan sorular                 |
| Galeri       | Görsel yükleme ve yönetimi                                    |
| Mesajlar     | İletişim formu mesajları                                      |
| Ayarlar      | İletişim bilgileri, sosyal medya, SEO, anasayfa metinleri     |
| Hesabım      | Parola değiştirme                                             |

## URL Yapısı

| URL                                   | İçerik                          |
|---------------------------------------|---------------------------------|
| `/`                                   | Anasayfa                        |
| `/hizmetler`                          | Hizmet listesi                  |
| `/hizmet/{slug}`                      | Hizmet detayı                   |
| `/hizmet/{slug}/{ilce}`               | İlçeye özel landing (dinamik)   |
| `/hakkimizda`, `/galeri`, `/iletisim` | Kurumsal sayfalar               |
| `/sayfa/{slug}`                       | Serbest sayfalar                |
| `/sitemap.xml`, `/robots.txt`         | SEO                             |
| `/icerik/...` (eski)                  | 301 ile yeni URL'e yönlendirir  |
| `/yonetim`                            | Yönetim paneli                  |

## Proje Yapısı

```
config/        Ayarlar, container (DI), rotalar
database/      Şemalar (mysql/sqlite), migrate & seed, başlangıç verileri
public/        Web kök dizini (index.php, .htaccess, assets)
src/
  Controllers/ Public ve Admin controller'ları
  Database/    PDO bağlantısı
  Middleware/  Auth, CSRF
  Repository/  Veri erişim katmanı
  Support/     Oturum, ayarlar, landing üreteci, yardımcılar
templates/     Twig şablonları (public + admin)
```

## Lisans

Özel (proprietary) — Çözüm Oto Elektrik için geliştirilmiştir.
