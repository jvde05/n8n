<?php

declare(strict_types=1);

/**
 * Şema kurulum scripti. .env'deki DB_DRIVER'a göre uygun schema dosyasını çalıştırır.
 * Kullanım: php database/migrate.php
 */

use App\Database\Database;
use Dotenv\Dotenv;

require __DIR__ . '/../vendor/autoload.php';

$root = dirname(__DIR__);
if (is_file($root . '/.env')) {
    Dotenv::createImmutable($root)->safeLoad();
}

$settings = require $root . '/config/settings.php';
$driver   = $settings['db']['driver'];
$pdo      = Database::fromConfig($settings['db']);

$schemaFile = $root . '/database/schema.' . $driver . '.sql';
if (!is_file($schemaFile)) {
    fwrite(STDERR, "Şema dosyası bulunamadı: {$schemaFile}\n");
    exit(1);
}

$sql = file_get_contents($schemaFile);

// SQLite çoklu ifadeyi exec ile çalıştırabilir; MySQL için noktalı virgülle bölüyoruz.
if ($driver === 'sqlite') {
    $pdo->exec($sql);
} else {
    foreach (array_filter(array_map('trim', explode(';', $sql))) as $stmt) {
        if ($stmt !== '' && !str_starts_with($stmt, '--')) {
            $pdo->exec($stmt);
        }
    }
}

echo "✓ Şema kuruldu ({$driver}).\n";
