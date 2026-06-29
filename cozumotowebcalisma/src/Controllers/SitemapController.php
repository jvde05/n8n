<?php

declare(strict_types=1);

namespace App\Controllers;

use App\Repository\DistrictRepository;
use App\Repository\PageRepository;
use App\Repository\ServiceRepository;
use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;

/**
 * Dinamik sitemap.xml ve robots.txt üretir. Hizmet x İlçe sayfaları otomatik dahil edilir.
 */
final class SitemapController
{
    public function __construct(
        private readonly ServiceRepository $services,
        private readonly DistrictRepository $districts,
        private readonly PageRepository $pages,
        private readonly array $appConfig
    ) {
    }

    public function sitemap(Request $request, Response $response): Response
    {
        $base = $this->appConfig['url'] ?: $this->baseFromRequest($request);
        $urls = [];

        $add = static function (string $loc, string $priority = '0.7', string $freq = 'weekly') use (&$urls): void {
            $urls[] = compact('loc', 'priority', 'freq');
        };

        $add($base . '/', '1.0', 'daily');
        $add($base . '/hizmetler', '0.9');
        $add($base . '/hakkimizda');
        $add($base . '/galeri');
        $add($base . '/iletisim', '0.8');

        $districts = $this->districts->allActive();

        foreach ($this->services->allActive() as $service) {
            $add($base . '/hizmet/' . $service['slug'], '0.9');
            if ((int) $service['enable_districts'] === 1) {
                foreach ($districts as $district) {
                    $add($base . '/hizmet/' . $service['slug'] . '/' . $district['slug'], '0.6');
                }
            }
        }

        foreach ($this->pages->all() as $page) {
            // hakkimizda kendi özel URL'inde (/hakkimizda) zaten listelendi.
            if ((int) $page['is_active'] === 1 && $page['slug'] !== 'hakkimizda') {
                $add($base . '/sayfa/' . $page['slug']);
            }
        }

        $xml = '<?xml version="1.0" encoding="UTF-8"?>' . "\n";
        $xml .= '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' . "\n";
        foreach ($urls as $u) {
            $xml .= "  <url>\n";
            $xml .= '    <loc>' . htmlspecialchars($u['loc'], ENT_XML1) . "</loc>\n";
            $xml .= '    <changefreq>' . $u['freq'] . "</changefreq>\n";
            $xml .= '    <priority>' . $u['priority'] . "</priority>\n";
            $xml .= "  </url>\n";
        }
        $xml .= '</urlset>';

        $response->getBody()->write($xml);
        return $response->withHeader('Content-Type', 'application/xml; charset=utf-8');
    }

    public function robots(Request $request, Response $response): Response
    {
        $base = $this->appConfig['url'] ?: $this->baseFromRequest($request);
        $txt  = "User-agent: *\nAllow: /\nDisallow: /yonetim\n\nSitemap: {$base}/sitemap.xml\n";
        $response->getBody()->write($txt);
        return $response->withHeader('Content-Type', 'text/plain; charset=utf-8');
    }

    private function baseFromRequest(Request $request): string
    {
        $uri = $request->getUri();
        $base = $uri->getScheme() . '://' . $uri->getHost();
        if ($uri->getPort() && !in_array($uri->getPort(), [80, 443], true)) {
            $base .= ':' . $uri->getPort();
        }
        return $base;
    }
}
