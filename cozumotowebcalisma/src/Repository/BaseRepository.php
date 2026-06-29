<?php

declare(strict_types=1);

namespace App\Repository;

use PDO;

abstract class BaseRepository
{
    public function __construct(protected readonly PDO $pdo)
    {
    }

    protected function isMysql(): bool
    {
        return $this->pdo->getAttribute(PDO::ATTR_DRIVER_NAME) === 'mysql';
    }

    /** SQLite/MySQL arasında geçerli "şimdi" zaman damgası. */
    protected function now(): string
    {
        return date('Y-m-d H:i:s');
    }
}
