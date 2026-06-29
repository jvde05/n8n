<?php

declare(strict_types=1);

namespace App\Repository;

final class UserRepository extends BaseRepository
{
    public function findByEmail(string $email): ?array
    {
        $stmt = $this->pdo->prepare('SELECT * FROM users WHERE email = :e');
        $stmt->execute(['e' => $email]);
        return $stmt->fetch() ?: null;
    }

    public function find(int $id): ?array
    {
        $stmt = $this->pdo->prepare('SELECT * FROM users WHERE id = :id');
        $stmt->execute(['id' => $id]);
        return $stmt->fetch() ?: null;
    }

    public function create(string $name, string $email, string $password, string $role = 'admin'): int
    {
        $stmt = $this->pdo->prepare(
            'INSERT INTO users (name, email, password_hash, role, created_at) VALUES (:n, :e, :p, :r, :c)'
        );
        $stmt->execute([
            'n' => $name,
            'e' => $email,
            'p' => password_hash($password, PASSWORD_DEFAULT),
            'r' => $role,
            'c' => $this->now(),
        ]);
        return (int) $this->pdo->lastInsertId();
    }

    public function updatePassword(int $id, string $password): void
    {
        $this->pdo->prepare('UPDATE users SET password_hash = :p WHERE id = :id')
            ->execute(['p' => password_hash($password, PASSWORD_DEFAULT), 'id' => $id]);
    }

    public function exists(string $email): bool
    {
        return $this->findByEmail($email) !== null;
    }
}
