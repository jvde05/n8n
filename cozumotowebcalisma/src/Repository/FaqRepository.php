<?php

declare(strict_types=1);

namespace App\Repository;

final class FaqRepository extends BaseRepository
{
    /** Genel SSS (hizmete bağlı olmayan). */
    public function general(): array
    {
        return $this->pdo->query(
            'SELECT * FROM faqs WHERE service_id IS NULL AND is_active = 1 ORDER BY sort_order ASC, id ASC'
        )->fetchAll();
    }

    public function forService(int $serviceId): array
    {
        $stmt = $this->pdo->prepare(
            'SELECT * FROM faqs WHERE service_id = :s AND is_active = 1 ORDER BY sort_order ASC, id ASC'
        );
        $stmt->execute(['s' => $serviceId]);
        return $stmt->fetchAll();
    }

    public function all(): array
    {
        return $this->pdo->query(
            'SELECT f.*, s.title AS service_title FROM faqs f
             LEFT JOIN services s ON s.id = f.service_id
             ORDER BY f.sort_order ASC, f.id ASC'
        )->fetchAll();
    }

    public function find(int $id): ?array
    {
        $stmt = $this->pdo->prepare('SELECT * FROM faqs WHERE id = :id');
        $stmt->execute(['id' => $id]);
        return $stmt->fetch() ?: null;
    }

    public function create(array $d): int
    {
        $stmt = $this->pdo->prepare(
            'INSERT INTO faqs (service_id, question, answer, sort_order, is_active)
             VALUES (:s, :q, :a, :o, :act)'
        );
        $stmt->execute($this->bind($d));
        return (int) $this->pdo->lastInsertId();
    }

    public function update(int $id, array $d): void
    {
        $stmt = $this->pdo->prepare(
            'UPDATE faqs SET service_id = :s, question = :q, answer = :a, sort_order = :o, is_active = :act WHERE id = :id'
        );
        $params = $this->bind($d);
        $params['id'] = $id;
        $stmt->execute($params);
    }

    public function delete(int $id): void
    {
        $this->pdo->prepare('DELETE FROM faqs WHERE id = :id')->execute(['id' => $id]);
    }

    private function bind(array $d): array
    {
        $serviceId = $d['service_id'] ?? null;
        return [
            's' => $serviceId === '' || $serviceId === null ? null : (int) $serviceId,
            'q' => $d['question'],
            'a' => $d['answer'],
            'o' => (int) ($d['sort_order'] ?? 0),
            'act' => (int) ($d['is_active'] ?? 1),
        ];
    }
}
