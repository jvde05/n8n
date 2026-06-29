<?php

declare(strict_types=1);

namespace App\Support;

/**
 * Oturum, flash mesajları ve CSRF token yönetimi için ince sarmalayıcı.
 */
final class Session
{
    public static function start(string $name): void
    {
        if (session_status() === PHP_SESSION_ACTIVE) {
            return;
        }
        session_name($name);
        session_set_cookie_params([
            'httponly' => true,
            'samesite' => 'Lax',
            'secure'   => ($_SERVER['HTTPS'] ?? '') === 'on',
            'path'     => '/',
        ]);
        session_start();
    }

    public static function get(string $key, mixed $default = null): mixed
    {
        return $_SESSION[$key] ?? $default;
    }

    public static function set(string $key, mixed $value): void
    {
        $_SESSION[$key] = $value;
    }

    public static function forget(string $key): void
    {
        unset($_SESSION[$key]);
    }

    public static function regenerate(): void
    {
        session_regenerate_id(true);
    }

    public static function destroy(): void
    {
        $_SESSION = [];
        if (session_status() === PHP_SESSION_ACTIVE) {
            session_destroy();
        }
    }

    /** Tek seferlik flash mesaj ekler. */
    public static function flash(string $type, string $message): void
    {
        $_SESSION['_flash'][] = ['type' => $type, 'message' => $message];
    }

    /** Birikmiş flash mesajları döndürür ve temizler. */
    public static function takeFlash(): array
    {
        $flash = $_SESSION['_flash'] ?? [];
        unset($_SESSION['_flash']);
        return $flash;
    }

    public static function csrfToken(): string
    {
        if (empty($_SESSION['_csrf'])) {
            $_SESSION['_csrf'] = bin2hex(random_bytes(32));
        }
        return $_SESSION['_csrf'];
    }

    public static function verifyCsrf(?string $token): bool
    {
        return is_string($token)
            && !empty($_SESSION['_csrf'])
            && hash_equals($_SESSION['_csrf'], $token);
    }

    public static function isAuthenticated(): bool
    {
        return !empty($_SESSION['user_id']);
    }

    public static function user(): ?array
    {
        return $_SESSION['user'] ?? null;
    }
}
