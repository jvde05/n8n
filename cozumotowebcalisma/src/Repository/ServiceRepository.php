<?php

declare(strict_types=1);

namespace App\Repository;

final class ServiceRepository extends BaseRepository
{
    public function allActive(): array
    {
        return $this->pdo->query(
            'SELECT * FROM services WHERE is_active = 1 ORDER BY sort_order ASC, id ASC'
        )->fetchAll();
    }

    public function all(): array
    {
        return $this->pdo->query(
            'SELECT * FROM services ORDER BY sort_order ASC, id ASC'
        )->fetchAll();
    }

    public function find(int $id): ?array
    {
        $stmt = $this->pdo->prepare('SELECT * FROM services WHERE id = :id');
        $stmt->execute(['id' => $id]);
        return $stmt->fetch() ?: null;
    }

    public function findBySlug(string $slug): ?array
    {
        $stmt = $this->pdo->prepare('SELECT * FROM services WHERE slug = :slug AND is_active = 1');
        $stmt->execute(['slug' => $slug]);
        return $stmt->fetch() ?: null;
    }

    public function create(array $data): int
    {
        $sql = 'INSERT INTO services
            (slug, title, summary, body, icon, image, meta_title, meta_description, sort_order, is_active, enable_districts, created_at, updated_at)
            VALUES (:slug, :title, :summary, :body, :icon, :image, :meta_title, :meta_description, :sort_order, :is_active, :enable_districts, :created_at, :updated_at)';
        $stmt = $this->pdo->prepare($sql);
        $stmt->execute($this->bind($data));
        return (int) $this->pdo->lastInsertId();
    }

    public function update(int $id, array $data): void
    {
        $sql = 'UPDATE services SET
            slug = :slug, title = :title, summary = :summary, body = :body, icon = :icon, image = :image,
            meta_title = :meta_title, meta_description = :meta_description, sort_order = :sort_order,
            is_active = :is_active, enable_districts = :enable_districts, updated_at = :updated_at
            WHERE id = :id';
        $params = $this->bind($data);
        unset($params['created_at']);
        $params['id'] = $id;
        $this->pdo->prepare($sql)->execute($params);
    }

    public function delete(int $id): void
    {
        $this->pdo->prepare('DELETE FROM services WHERE id = :id')->execute(['id' => $id]);
    }

    private function bind(array $d): array
    {
        $now = $this->now();
        return [
            'slug'             => $d['slug'],
            'title'            => $d['title'],
            'summary'          => $d['summary'] ?? null,
            'body'             => $d['body'] ?? null,
            'icon'             => $d['icon'] ?? null,
            'image'            => $d['image'] ?? null,
            'meta_title'       => $d['meta_title'] ?? null,
            'meta_description' => $d['meta_description'] ?? null,
            'sort_order'       => (int) ($d['sort_order'] ?? 0),
            'is_active'        => (int) ($d['is_active'] ?? 1),
            'enable_districts' => (int) ($d['enable_districts'] ?? 1),
            'created_at'       => $d['created_at'] ?? $now,
            'updated_at'       => $now,
        ];
    }
}
