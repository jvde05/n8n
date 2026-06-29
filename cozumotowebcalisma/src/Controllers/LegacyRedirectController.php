<?php

declare(strict_types=1);

namespace App\Controllers;

use App\Repository\DistrictRepository;
use App\Repository\ServiceRepository;
use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;

/**
 * Eski CMS URL'lerini (/icerik/...) yeni temiz URL'lere 301 ile yönlendirir.
 * SEO değerini korumak için en iyi eşleşmeyi bulmaya çalışır.
 */
final class LegacyRedirectController
{
    /** Eski slug anahtar kelimesi => yeni hizmet slug'ı. Uzun ifadeler önce gelir. */
    private const SERVICE_MAP = [
        'edc-sanziman-servisi'      => 'edc-sanziman',
        'edc-sanziman'              => 'edc-sanziman',
        'edc-beyin-tamiri'          => 'edc-beyin',
        'edc-beyin'                 => 'edc-beyin',
        'kavrama-tamiri'            => 'kavrama',
        'kavrama-tamir'             => 'kavrama',
        'kavrama'                   => 'kavrama',
        'otomatik-sanziman-tamiri'  => 'dw5-otomatik-sanziman',
        'dw5-sanziman-onarim'       => 'dw5-otomatik-sanziman',
        'egr-temizleme'             => 'egr',
        'egr'                       => 'egr',
        'partikul-temizligi'        => 'partikul-filtre-temizligi',
        'partikul-filtre-temizligi' => 'partikul-filtre-temizligi',
        'adblue'                    => 'adblue',
        'eco-performans-yazilimlari' => 'eco-performans-yazilimlari',
        'airbag-onarimi'            => 'airbag-onarimi',
        'enjeksiyon-beyin-onarimi'  => 'enjeksiyon-beyin-onarimi',
    ];

    private const PAGE_MAP = [
        'anasayfa'      => '/',
        'hizmetlerimiz' => '/hizmetler',
        'hakkimizda'    => '/hakkimizda',
    ];

    public function __construct(
        private readonly ServiceRepository $services,
        private readonly DistrictRepository $districts
    ) {
    }

    public function handle(Request $request, Response $response, array $args): Response
    {
        $raw  = (string) ($args['rest'] ?? '');
        $slug = $this->extractSlug($raw);
        $target = $this->resolve($slug);

        return $response->withHeader('Location', $target)->withStatus(301);
    }

    private function extractSlug(string $raw): string
    {
        // /icerik/391/17/edc-sanziman  veya  icerik-401-17-bahcesehir-...  veya icerik40417yakuplu-...
        $s = trim($raw, '/');
        // Slash'lı format: son segmenti al.
        if (str_contains($s, '/')) {
            $parts = explode('/', $s);
            $s = end($parts);
        } else {
            // Tireli/birleşik format: baştaki "icerik", id ve kategori (17) parçalarını temizle.
            $s = preg_replace('/^icerik[-_]?/i', '', $s);
            $s = preg_replace('/^\d+[-_]?17[-_]?/', '', $s);
            $s = preg_replace('/^\d+[-_]?/', '', $s);
        }

        return $this->normalize($s);
    }

    private function normalize(string $s): string
    {
        $tr = ['ı' => 'i', 'İ' => 'i', 'ş' => 's', 'Ş' => 's', 'ğ' => 'g', 'Ğ' => 'g',
               'ü' => 'u', 'Ü' => 'u', 'ö' => 'o', 'Ö' => 'o', 'ç' => 'c', 'Ç' => 'c'];
        $s = strtr($s, $tr);
        $s = mb_strtolower($s, 'UTF-8');
        $s = preg_replace('/[^a-z0-9]+/', '-', $s);
        return trim((string) $s, '-');
    }

    private function resolve(string $slug): string
    {
        if ($slug === '' ) {
            return '/';
        }

        if (isset(self::PAGE_MAP[$slug])) {
            return self::PAGE_MAP[$slug];
        }

        // Doğrudan hizmet eşleşmesi.
        foreach (self::SERVICE_MAP as $key => $newSlug) {
            if ($slug === $key) {
                return '/hizmet/' . $newSlug;
            }
        }

        // İlçe öneki + hizmet (örn. esenyurt-edc-sanziman-servisi).
        foreach ($this->districts->allActive() as $district) {
            $prefix = $this->normalize($district['slug']);
            if (str_starts_with($slug, $prefix . '-')) {
                $remainder = substr($slug, strlen($prefix) + 1);
                foreach (self::SERVICE_MAP as $key => $newSlug) {
                    if ($remainder === $key) {
                        return '/hizmet/' . $newSlug . '/' . $district['slug'];
                    }
                }
            }
        }

        // Suffix bazlı son çare: slug bir hizmet anahtarıyla bitiyorsa.
        foreach (self::SERVICE_MAP as $key => $newSlug) {
            if (str_ends_with($slug, $key)) {
                return '/hizmet/' . $newSlug;
            }
        }

        return '/hizmetler';
    }
}
