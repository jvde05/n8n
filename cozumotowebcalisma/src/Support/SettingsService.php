<?php

declare(strict_types=1);

namespace App\Support;

use PDO;

/**
 * settings tablosundaki anahtar/değer çiftlerini yönetir (telefon, adres, sosyal medya vb.).
 */
final class SettingsService
{
    private ?array $cache = null;

    public function __construct(private readonly PDO $pdo)
    {
    }

    public function all(): array
    {
        if ($this->cache !== null) {
            return $this->cache;
        }

        $rows = $this->pdo->query('SELECT `key`, `value` FROM settings')->fetchAll();
        $out = [];
        foreach ($rows as $row) {
            $out[$row['key']] = $row['value'];
        }

        return $this->cache = $out;
    }

    public function get(string $key, ?string $default = null): ?string
    {
        return $this->all()[$key] ?? $default;
    }

    public function set(string $key, ?string $value): void
    {
        $driver = $this->pdo->getAttribute(PDO::ATTR_DRIVER_NAME);
        $sql = $driver === 'mysql'
            ? 'INSERT INTO settings (`key`, `value`) VALUES (:k, :v)
               ON DUPLICATE KEY UPDATE `value` = :v2'
            : 'INSERT INTO settings (key, value) VALUES (:k, :v)
               ON CONFLICT(key) DO UPDATE SET value = :v2';

        $stmt = $this->pdo->prepare($sql);
        $stmt->execute(['k' => $key, 'v' => $value, 'v2' => $value]);
        $this->cache = null;
    }

    public function setMany(array $pairs): void
    {
        foreach ($pairs as $key => $value) {
            $this->set((string) $key, $value === null ? null : (string) $value);
        }
    }
}
