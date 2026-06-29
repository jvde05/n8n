<?php

declare(strict_types=1);

namespace App\Repository;

final class PageRepository extends BaseRepository
{
    public function all(): array
    {
        return $this->pdo->query('SELECT * FROM pages ORDER BY title ASC')->fetchAll();
    }

    public function find(int $id): ?array
    {
        $stmt = $this->pdo->prepare('SELECT * FROM pages WHERE id = :id');
        $stmt->execute(['id' => $id]);
        return $stmt->fetch() ?: null;
    }

    public function findBySlug(string $slug): ?array
    {
        $stmt = $this->pdo->prepare('SELECT * FROM pages WHERE slug = :slug AND is_active = 1');
        $stmt->execute(['slug' => $slug]);
        return $stmt->fetch() ?: null;
    }

    public function create(array $d): int
    {
        $stmt = $this->pdo->prepare(
            'INSERT INTO pages (slug, title, body, meta_title, meta_description, is_active, updated_at)
             VALUES (:slug, :title, :body, :mt, :md, :a, :u)'
        );
        $stmt->execute($this->bind($d));
        return (int) $this->pdo->lastInsertId();
    }

    public function update(int $id, array $d): void
    {
        $stmt = $this->pdo->prepare(
            'UPDATE pages SET slug = :slug, title = :title, body = :body, meta_title = :mt,
             meta_description = :md, is_active = :a, updated_at = :u WHERE id = :id'
        );
        $params = $this->bind($d);
        $params['id'] = $id;
        $stmt->execute($params);
    }

    public function delete(int $id): void
    {
        $this->pdo->prepare('DELETE FROM pages WHERE id = :id')->execute(['id' => $id]);
    }

    private function bind(array $d): array
    {
        return [
            'slug' => $d['slug'],
            'title' => $d['title'],
            'body' => $d['body'] ?? null,
            'mt' => $d['meta_title'] ?? null,
            'md' => $d['meta_description'] ?? null,
            'a' => (int) ($d['is_active'] ?? 1),
            'u' => $this->now(),
        ];
    }
}
