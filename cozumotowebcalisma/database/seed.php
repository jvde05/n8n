<?php

declare(strict_types=1);

/**
 * Başlangıç verilerini yükler: yönetici, site ayarları, hizmetler, ilçeler, sayfalar, SSS.
 * Kullanım: php database/seed.php
 * Hizmet/ilçe/sayfa verileri yalnızca ilgili tablo boşsa eklenir (yinelemeyi önler).
 * Ayarlar ve yönetici her çalıştırmada güncellenir (upsert).
 */

use App\Database\Database;
use App\Repository\UserRepository;
use App\Support\SettingsService;
use App\Support\Str;
use Dotenv\Dotenv;

require __DIR__ . '/../vendor/autoload.php';

$root = dirname(__DIR__);
if (is_file($root . '/.env')) {
    Dotenv::createImmutable($root)->safeLoad();
}

$config = require $root . '/config/settings.php';
$pdo    = Database::fromConfig($config['db']);

/* ---------------- Yönetici ---------------- */
$users = new UserRepository($pdo);
$adminEmail = $_ENV['ADMIN_EMAIL'] ?? 'admin@cozumoto.local';
if (!$users->exists($adminEmail)) {
    $users->create(
        $_ENV['ADMIN_NAME'] ?? 'Site Yöneticisi',
        $adminEmail,
        $_ENV['ADMIN_PASSWORD'] ?? 'Degistir123!'
    );
    echo "✓ Yönetici oluşturuldu: {$adminEmail}\n";
} else {
    echo "• Yönetici zaten mevcut: {$adminEmail}\n";
}

/* ---------------- Site ayarları ---------------- */
$settings = new SettingsService($pdo);
$settings->setMany([
    'brand_name'       => 'Çözüm Oto Elektrik',
    'site_title'       => 'Çözüm Oto Elektrik — Renault EDC Şanzıman & Elektronik Servisi | Esenyurt',
    'site_description' => 'Renault EDC şanzıman, mekatronik beyin onarımı, kavrama, DW5 otomatik şanzıman, EGR ve partikül filtre temizliğinde garantili servis. Esenyurt / İstanbul. Aynı gün teslim.',
    'phone_primary'    => '0539 586 93 56',
    'phone_secondary'  => '0538 527 93 56',
    'whatsapp'         => '0539 586 93 56',
    'email'            => '',
    'address'          => 'Akşemsettin Mah. Doğan Araslı Bulvarı, Fatih Oto Sanayi Sitesi, 208 Sk. C-4 A Blok No:15, Esenyurt / İstanbul',
    'maps_url'         => 'https://maps.app.goo.gl/wJ6QUq3RA31boQDi8',
    'maps_embed'       => '',
    'working_hours'    => 'Pazartesi - Cumartesi 09:00 - 19:00',
    'instagram'        => '',
    'facebook'         => '',
    'twitter'          => '',
    'youtube'          => '',
    'linkedin'         => '',
    'pinterest'        => '',
    'hero_title'       => 'Renault EDC Şanzıman ve Oto Elektronik Çözüm Merkezi',
    'hero_subtitle'    => 'EDC şanzıman, mekatronik beyin onarımı, kavrama, EGR ve partikül filtre temizliğinde garantili işçilik. Aracınız aynı gün içinde teslim edilir.',
]);
echo "✓ Site ayarları kaydedildi.\n";

/* ---------------- Hizmetler ---------------- */
$serviceCount = (int) $pdo->query('SELECT COUNT(*) FROM services')->fetchColumn();
if ($serviceCount === 0) {
    $services = require __DIR__ . '/seed_data/services.php';
    $stmt = $pdo->prepare(
        'INSERT INTO services (slug, title, summary, body, icon, meta_title, meta_description, sort_order, is_active, enable_districts, created_at, updated_at)
         VALUES (:slug, :title, :summary, :body, :icon, :meta_title, :meta_description, :sort_order, 1, :enable_districts, :now, :now)'
    );
    $now = date('Y-m-d H:i:s');
    foreach ($services as $i => $s) {
        $stmt->execute([
            'slug' => $s['slug'],
            'title' => $s['title'],
            'summary' => $s['summary'],
            'body' => $s['body'],
            'icon' => $s['icon'],
            'meta_title' => $s['meta_title'] ?? null,
            'meta_description' => $s['meta_description'] ?? null,
            'sort_order' => $i + 1,
            'enable_districts' => $s['enable_districts'] ?? 1,
            'now' => $now,
        ]);
    }
    echo '✓ ' . count($services) . " hizmet eklendi.\n";
} else {
    echo "• Hizmetler zaten mevcut ({$serviceCount}). Atlanıyor.\n";
}

/* ---------------- İlçeler ---------------- */
$districtCount = (int) $pdo->query('SELECT COUNT(*) FROM districts')->fetchColumn();
if ($districtCount === 0) {
    $districts = [
        'Esenyurt', 'Avcılar', 'Bahçeşehir', 'Beylikdüzü', 'Büyükçekmece', 'Yakuplu',
        'Haramidere', 'Küçükçekmece', 'Gürpınar', 'Mimarsinan', 'Bakırköy', 'Topkapı',
        'Sefaköy', 'Bahçelievler', 'İkitelli', 'Güngören', 'Merter', 'Zeytinburnu',
    ];
    $stmt = $pdo->prepare('INSERT INTO districts (slug, name, sort_order, is_active) VALUES (:slug, :name, :sort, 1)');
    foreach ($districts as $i => $name) {
        $stmt->execute(['slug' => Str::slug($name), 'name' => $name, 'sort' => $i + 1]);
    }
    echo '✓ ' . count($districts) . " ilçe eklendi.\n";
} else {
    echo "• İlçeler zaten mevcut ({$districtCount}). Atlanıyor.\n";
}

/* ---------------- Sayfalar ---------------- */
$pageCount = (int) $pdo->query('SELECT COUNT(*) FROM pages')->fetchColumn();
if ($pageCount === 0) {
    $pages = require __DIR__ . '/seed_data/pages.php';
    $stmt = $pdo->prepare(
        'INSERT INTO pages (slug, title, body, meta_title, meta_description, is_active, updated_at)
         VALUES (:slug, :title, :body, :mt, :md, 1, :now)'
    );
    foreach ($pages as $p) {
        $stmt->execute([
            'slug' => $p['slug'], 'title' => $p['title'], 'body' => $p['body'],
            'mt' => $p['meta_title'] ?? null, 'md' => $p['meta_description'] ?? null,
            'now' => date('Y-m-d H:i:s'),
        ]);
    }
    echo '✓ ' . count($pages) . " sayfa eklendi.\n";
} else {
    echo "• Sayfalar zaten mevcut ({$pageCount}). Atlanıyor.\n";
}

/* ---------------- SSS ---------------- */
$faqCount = (int) $pdo->query('SELECT COUNT(*) FROM faqs')->fetchColumn();
if ($faqCount === 0) {
    $faqs = require __DIR__ . '/seed_data/faqs.php';
    $stmt = $pdo->prepare(
        'INSERT INTO faqs (service_id, question, answer, sort_order, is_active) VALUES (NULL, :q, :a, :o, 1)'
    );
    foreach ($faqs as $i => $f) {
        $stmt->execute(['q' => $f['q'], 'a' => $f['a'], 'o' => $i + 1]);
    }
    echo '✓ ' . count($faqs) . " SSS eklendi.\n";
} else {
    echo "• SSS zaten mevcut ({$faqCount}). Atlanıyor.\n";
}

echo "\nSeed tamamlandı.\n";
