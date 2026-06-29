<?php

declare(strict_types=1);

namespace App\Repository;

final class MessageRepository extends BaseRepository
{
    public function create(array $d): int
    {
        $stmt = $this->pdo->prepare(
            'INSERT INTO messages (name, phone, email, subject, body, is_read, created_at)
             VALUES (:n, :p, :e, :s, :b, 0, :c)'
        );
        $stmt->execute([
            'n' => $d['name'],
            'p' => $d['phone'] ?? null,
            'e' => $d['email'] ?? null,
            's' => $d['subject'] ?? null,
            'b' => $d['body'],
            'c' => $this->now(),
        ]);
        return (int) $this->pdo->lastInsertId();
    }

    public function all(): array
    {
        return $this->pdo->query('SELECT * FROM messages ORDER BY created_at DESC, id DESC')->fetchAll();
    }

    public function find(int $id): ?array
    {
        $stmt = $this->pdo->prepare('SELECT * FROM messages WHERE id = :id');
        $stmt->execute(['id' => $id]);
        return $stmt->fetch() ?: null;
    }

    public function unreadCount(): int
    {
        return (int) $this->pdo->query('SELECT COUNT(*) FROM messages WHERE is_read = 0')->fetchColumn();
    }

    public function markRead(int $id): void
    {
        $this->pdo->prepare('UPDATE messages SET is_read = 1 WHERE id = :id')->execute(['id' => $id]);
    }

    public function delete(int $id): void
    {
        $this->pdo->prepare('DELETE FROM messages WHERE id = :id')->execute(['id' => $id]);
    }
}
