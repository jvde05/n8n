<?php

declare(strict_types=1);

namespace App\Support;

/**
 * Hizmet + İlçe için dinamik landing içeriği ve SEO meta verileri üretir.
 * Admin panelden özel override girilmemişse şablondan profesyonel metin oluşturur.
 */
final class LandingBuilder
{
    public function __construct(private readonly SettingsService $settings)
    {
    }

    public function metaTitle(array $service, array $district): string
    {
        return sprintf('%s %s | %s', $district['name'], $service['title'], $this->brand());
    }

    public function metaDescription(array $service, array $district): string
    {
        return sprintf(
            '%s bölgesinde %s hizmeti. %s olarak garantili, aynı gün teslim. Hemen arayın: %s',
            $district['name'],
            mb_strtolower($service['title'], 'UTF-8'),
            $this->brand(),
            $this->settings->get('phone_primary', '')
        );
    }

    public function heading(array $service, array $district): string
    {
        return sprintf('%s %s', $district['name'], $service['title']);
    }

    /**
     * Override yoksa kullanılacak HTML gövde. Hizmetin kendi içeriğini
     * ilçeye özel bir giriş paragrafıyla birleştirir.
     */
    public function body(array $service, array $district): string
    {
        $brand   = $this->brand();
        $name    = htmlspecialchars($district['name'], ENT_QUOTES, 'UTF-8');
        $title   = htmlspecialchars($service['title'], ENT_QUOTES, 'UTF-8');
        $titleLc = mb_strtolower($service['title'], 'UTF-8');
        $phone   = htmlspecialchars((string) $this->settings->get('phone_primary', ''), ENT_QUOTES, 'UTF-8');

        $intro = "<p><strong>{$name} {$title}</strong> hizmeti için {$brand} doğru adrestir. "
            . "{$name} ve çevresinden gelen araç sahiplerine, uzman ekibimiz ve güncel cihaz parkurumuzla "
            . "garantili {$titleLc} çözümleri sunuyoruz. Aracınız aynı gün içinde, sorunsuz şekilde teslim edilir.</p>";

        $body = trim((string) ($service['body'] ?? ''));

        $cta = "<p>{$name} bölgesinde {$titleLc} için hemen bizi arayın: "
            . "<a href=\"tel:{$phone}\">{$phone}</a> — ücretsiz ön değerlendirme yapıyoruz.</p>";

        return $intro . $body . $cta;
    }

    private function brand(): string
    {
        return $this->settings->get('brand_name', 'Çözüm Oto Elektrik');
    }
}
