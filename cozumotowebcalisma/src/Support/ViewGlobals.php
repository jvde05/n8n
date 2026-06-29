<?php

declare(strict_types=1);

namespace App\Support;

use App\Repository\ServiceRepository;
use Slim\Views\Twig;
use Twig\TwigFilter;
use Twig\TwigFunction;

/**
 * Tüm Twig şablonlarına ortak değişken ve fonksiyonları ekler.
 */
final class ViewGlobals
{
    public function __construct(
        private readonly SettingsService $settings,
        private readonly ServiceRepository $services,
        private readonly array $appConfig
    ) {
    }

    public function apply(Twig $twig): void
    {
        $env = $twig->getEnvironment();

        $twig->getEnvironment()->addGlobal('site', $this->settings->all());
        $twig->getEnvironment()->addGlobal('app', [
            'name' => $this->appConfig['name'],
            'url'  => $this->appConfig['url'],
            'year' => (int) date('Y'),
        ]);
        // Menü için aktif hizmetler.
        $twig->getEnvironment()->addGlobal('menu_services', $this->services->allActive());

        // WhatsApp linki üreteci.
        $env->addFunction(new TwigFunction('whatsapp_link', function (?string $text = null): string {
            $phone = preg_replace('/\D+/', '', (string) $this->settings->get('whatsapp', ''));
            if ($phone !== '' && !str_starts_with($phone, '90')) {
                $phone = '90' . ltrim($phone, '0');
            }
            $url = 'https://api.whatsapp.com/send?phone=' . $phone;
            if ($text) {
                $url .= '&text=' . rawurlencode($text);
            }
            return $url;
        }));

        // Telefonu tel: formatına çevirir.
        $env->addFunction(new TwigFunction('tel_link', function (string $phone): string {
            $digits = preg_replace('/\D+/', '', $phone);
            if (!str_starts_with($digits, '90') && strlen($digits) === 10) {
                $digits = '90' . $digits;
            }
            return 'tel:+' . $digits;
        }));

        // Metni güvenli özet haline getirir.
        $env->addFilter(new TwigFilter('excerpt', function (?string $html, int $len = 160): string {
            $text = trim(preg_replace('/\s+/', ' ', strip_tags((string) $html)));
            return mb_strlen($text) > $len ? mb_substr($text, 0, $len - 1) . '…' : $text;
        }));
    }
}
