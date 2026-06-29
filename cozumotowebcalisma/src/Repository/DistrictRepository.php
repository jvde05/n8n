<?php

declare(strict_types=1);

namespace App\Repository;

final class DistrictRepository extends BaseRepository
{
    public function allActive(): array
    {
        return $this->pdo->query(
            'SELECT * FROM districts WHERE is_active = 1 ORDER BY sort_order ASC, name ASC'
        )->fetchAll();
    }

    public function all(): array
    {
        return $this->pdo->query('SELECT * FROM districts ORDER BY sort_order ASC, name ASC')->fetchAll();
    }

    public function find(int $id): ?array
    {
        $stmt = $this->pdo->prepare('SELECT * FROM districts WHERE id = :id');
        $stmt->execute(['id' => $id]);
        return $stmt->fetch() ?: null;
    }

    public function findBySlug(string $slug): ?array
    {
        $stmt = $this->pdo->prepare('SELECT * FROM districts WHERE slug = :slug AND is_active = 1');
        $stmt->execute(['slug' => $slug]);
        return $stmt->fetch() ?: null;
    }

    public function create(array $d): int
    {
        $stmt = $this->pdo->prepare(
            'INSERT INTO districts (slug, name, sort_order, is_active) VALUES (:slug, :name, :sort_order, :is_active)'
        );
        $stmt->execute([
            'slug' => $d['slug'],
            'name' => $d['name'],
            'sort_order' => (int) ($d['sort_order'] ?? 0),
            'is_active' => (int) ($d['is_active'] ?? 1),
        ]);
        return (int) $this->pdo->lastInsertId();
    }

    public function update(int $id, array $d): void
    {
        $stmt = $this->pdo->prepare(
            'UPDATE districts SET slug = :slug, name = :name, sort_order = :sort_order, is_active = :is_active WHERE id = :id'
        );
        $stmt->execute([
            'slug' => $d['slug'],
            'name' => $d['name'],
            'sort_order' => (int) ($d['sort_order'] ?? 0),
            'is_active' => (int) ($d['is_active'] ?? 1),
            'id' => $id,
        ]);
    }

    public function delete(int $id): void
    {
        $this->pdo->prepare('DELETE FROM districts WHERE id = :id')->execute(['id' => $id]);
    }
}
