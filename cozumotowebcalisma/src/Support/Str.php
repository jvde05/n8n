<?php

declare(strict_types=1);

namespace App\Support;

final class Str
{
    /** Türkçe karakterleri sadeleştirerek URL-dostu slug üretir. */
    public static function slug(string $value): string
    {
        $tr = ['ı' => 'i', 'İ' => 'i', 'ş' => 's', 'Ş' => 's', 'ğ' => 'g', 'Ğ' => 'g',
               'ü' => 'u', 'Ü' => 'u', 'ö' => 'o', 'Ö' => 'o', 'ç' => 'c', 'Ç' => 'c'];
        $value = strtr($value, $tr);
        $value = mb_strtolower($value, 'UTF-8');
        $value = preg_replace('/[^a-z0-9]+/', '-', $value);
        return trim((string) $value, '-');
    }
}
