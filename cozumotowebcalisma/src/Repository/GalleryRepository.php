<?php

declare(strict_types=1);

namespace App\Repository;

final class GalleryRepository extends BaseRepository
{
    public function allActive(): array
    {
        return $this->pdo->query(
            'SELECT * FROM gallery WHERE is_active = 1 ORDER BY sort_order ASC, id DESC'
        )->fetchAll();
    }

    public function all(): array
    {
        return $this->pdo->query('SELECT * FROM gallery ORDER BY sort_order ASC, id DESC')->fetchAll();
    }

    public function find(int $id): ?array
    {
        $stmt = $this->pdo->prepare('SELECT * FROM gallery WHERE id = :id');
        $stmt->execute(['id' => $id]);
        return $stmt->fetch() ?: null;
    }

    public function create(array $d): int
    {
        $stmt = $this->pdo->prepare(
            'INSERT INTO gallery (title, file_path, sort_order, is_active, created_at)
             VALUES (:t, :f, :o, :a, :c)'
        );
        $stmt->execute([
            't' => $d['title'] ?? null,
            'f' => $d['file_path'],
            'o' => (int) ($d['sort_order'] ?? 0),
            'a' => (int) ($d['is_active'] ?? 1),
            'c' => $this->now(),
        ]);
        return (int) $this->pdo->lastInsertId();
    }

    public function delete(int $id): void
    {
        $this->pdo->prepare('DELETE FROM gallery WHERE id = :id')->execute(['id' => $id]);
    }
}
