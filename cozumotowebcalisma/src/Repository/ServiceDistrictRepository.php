<?php

declare(strict_types=1);

namespace App\Repository;

/**
 * Hizmet x İlçe için isteğe bağlı özel içerik override'larını yönetir.
 */
final class ServiceDistrictRepository extends BaseRepository
{
    public function findPair(int $serviceId, int $districtId): ?array
    {
        $stmt = $this->pdo->prepare(
            'SELECT * FROM service_district WHERE service_id = :s AND district_id = :d AND is_active = 1'
        );
        $stmt->execute(['s' => $serviceId, 'd' => $districtId]);
        return $stmt->fetch() ?: null;
    }

    public function upsert(int $serviceId, int $districtId, array $d): void
    {
        $existing = $this->pdo->prepare(
            'SELECT id FROM service_district WHERE service_id = :s AND district_id = :d'
        );
        $existing->execute(['s' => $serviceId, 'd' => $districtId]);
        $id = $existing->fetchColumn();

        if ($id) {
            $stmt = $this->pdo->prepare(
                'UPDATE service_district SET body = :body, meta_title = :mt, meta_description = :md, is_active = :a WHERE id = :id'
            );
            $stmt->execute([
                'body' => $d['body'] ?? null,
                'mt' => $d['meta_title'] ?? null,
                'md' => $d['meta_description'] ?? null,
                'a' => (int) ($d['is_active'] ?? 1),
                'id' => $id,
            ]);
            return;
        }

        $stmt = $this->pdo->prepare(
            'INSERT INTO service_district (service_id, district_id, body, meta_title, meta_description, is_active)
             VALUES (:s, :d, :body, :mt, :md, :a)'
        );
        $stmt->execute([
            's' => $serviceId,
            'd' => $districtId,
            'body' => $d['body'] ?? null,
            'mt' => $d['meta_title'] ?? null,
            'md' => $d['meta_description'] ?? null,
            'a' => (int) ($d['is_active'] ?? 1),
        ]);
    }
}
