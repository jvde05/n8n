<?php

declare(strict_types=1);

namespace App\Database;

use PDO;
use RuntimeException;

/**
 * PDO bağlantı fabrikası. MySQL (production) ve SQLite (lokal) destekler.
 */
final class Database
{
    private static ?PDO $instance = null;

    public static function fromConfig(array $db): PDO
    {
        if (self::$instance instanceof PDO) {
            return self::$instance;
        }

        $options = [
            PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
            PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
            PDO::ATTR_EMULATE_PREPARES   => false,
        ];

        $driver = $db['driver'] ?? 'mysql';

        if ($driver === 'sqlite') {
            $path = $db['sqlite'];
            $dir  = dirname($path);
            if (!is_dir($dir)) {
                mkdir($dir, 0775, true);
            }
            $pdo = new PDO('sqlite:' . $path, null, null, $options);
            $pdo->exec('PRAGMA foreign_keys = ON');
        } elseif ($driver === 'mysql') {
            $dsn = sprintf(
                'mysql:host=%s;port=%d;dbname=%s;charset=%s',
                $db['host'],
                $db['port'],
                $db['name'],
                $db['charset']
            );
            $pdo = new PDO($dsn, $db['user'], $db['pass'], $options);
        } else {
            throw new RuntimeException("Desteklenmeyen veritabanı sürücüsü: {$driver}");
        }

        return self::$instance = $pdo;
    }
}
