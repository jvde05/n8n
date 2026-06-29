<?php

declare(strict_types=1);

namespace App\Controllers\Admin;

use App\Controllers\BaseController;
use App\Support\Session;
use App\Support\SettingsService;
use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;
use Slim\Views\Twig;

final class SettingController extends BaseController
{
    /** Yönetilebilir ayar anahtarları. */
    private const KEYS = [
        'brand_name', 'site_title', 'site_description',
        'phone_primary', 'phone_secondary', 'whatsapp', 'email',
        'address', 'maps_url', 'maps_embed',
        'working_hours',
        'instagram', 'facebook', 'twitter', 'youtube', 'linkedin', 'pinterest',
        'hero_title', 'hero_subtitle',
    ];

    public function __construct(Twig $view, private readonly SettingsService $settings)
    {
        parent::__construct($view);
    }

    public function edit(Request $request, Response $response): Response
    {
        return $this->render($response, 'admin/settings.twig', [
            'values' => $this->settings->all(),
            'keys'   => self::KEYS,
        ]);
    }

    public function update(Request $request, Response $response): Response
    {
        $data = (array) $request->getParsedBody();
        $pairs = [];
        foreach (self::KEYS as $key) {
            $pairs[$key] = isset($data[$key]) ? trim((string) $data[$key]) : '';
        }
        $this->settings->setMany($pairs);
        Session::flash('success', 'Ayarlar kaydedildi.');
        return $this->redirect($response, '/yonetim/ayarlar');
    }
}
