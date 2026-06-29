<?php

declare(strict_types=1);

/**
 * Uygulama ayarlarını .env üzerinden derler.
 * PHP-DI container bu diziyi 'settings' anahtarıyla okur.
 */

$root = dirname(__DIR__);

return [
    'app' => [
        'name'  => $_ENV['APP_NAME'] ?? 'Çözüm Oto Elektrik',
        'env'   => $_ENV['APP_ENV'] ?? 'production',
        'debug' => filter_var($_ENV['APP_DEBUG'] ?? false, FILTER_VALIDATE_BOOL),
        'url'   => rtrim($_ENV['APP_URL'] ?? '', '/'),
        'root'  => $root,
    ],

    'db' => [
        'driver'  => $_ENV['DB_DRIVER'] ?? 'mysql',
        'host'    => $_ENV['DB_HOST'] ?? '127.0.0.1',
        'port'    => (int) ($_ENV['DB_PORT'] ?? 3306),
        'name'    => $_ENV['DB_NAME'] ?? 'cozumoto',
        'user'    => $_ENV['DB_USER'] ?? 'root',
        'pass'    => $_ENV['DB_PASS'] ?? '',
        'charset' => $_ENV['DB_CHARSET'] ?? 'utf8mb4',
        'sqlite'  => $root . '/' . ltrim($_ENV['DB_SQLITE_PATH'] ?? 'database/cozumoto.sqlite', '/'),
    ],

    'session' => [
        'name' => $_ENV['SESSION_NAME'] ?? 'cozumoto_session',
    ],

    'twig' => [
        'templates' => $root . '/templates',
        'cache'     => filter_var($_ENV['APP_DEBUG'] ?? false, FILTER_VALIDATE_BOOL)
            ? false
            : $root . '/var/cache/twig',
    ],
];
