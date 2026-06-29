<?php

declare(strict_types=1);

use App\Controllers\ContactController;
use App\Controllers\GalleryController;
use App\Controllers\HomeController;
use App\Controllers\LegacyRedirectController;
use App\Controllers\PageController;
use App\Controllers\ServiceController;
use App\Controllers\SitemapController;
use App\Middleware\AuthMiddleware;
use Slim\App as SlimApp;
use Slim\Routing\RouteCollectorProxy;

return function (SlimApp $app): void {
    // ---- Genel (public) rotalar ----
    $app->get('/', [HomeController::class, 'index']);
    $app->get('/hizmetler', [ServiceController::class, 'index']);
    $app->get('/hizmet/{slug}', [ServiceController::class, 'show']);
    $app->get('/hizmet/{slug}/{district}', [ServiceController::class, 'showDistrict']);

    $app->get('/galeri', [GalleryController::class, 'index']);
    $app->get('/iletisim', [ContactController::class, 'show']);
    $app->post('/iletisim', [ContactController::class, 'submit']);

    // Hakkımızda ve diğer serbest sayfalar.
    $app->get('/hakkimizda', function ($req, $res) use ($app) {
        $controller = $app->getContainer()->get(PageController::class);
        return $controller->show($req, $res, ['slug' => 'hakkimizda']);
    });
    $app->get('/sayfa/{slug}', [PageController::class, 'show']);

    // SEO.
    $app->get('/sitemap.xml', [SitemapController::class, 'sitemap']);
    $app->get('/robots.txt', [SitemapController::class, 'robots']);

    // Eski CMS URL'leri için 301 yönlendirmeleri.
    $app->get('/icerik[/{rest:.*}]', [LegacyRedirectController::class, 'handle']);

    // ---- Yönetim paneli ----
    $app->get('/yonetim/giris', [App\Controllers\Admin\AuthController::class, 'showLogin']);
    $app->post('/yonetim/giris', [App\Controllers\Admin\AuthController::class, 'login']);
    $app->get('/yonetim/cikis', [App\Controllers\Admin\AuthController::class, 'logout']);

    $app->group('/yonetim', function (RouteCollectorProxy $g): void {
        $g->get('', [App\Controllers\Admin\DashboardController::class, 'index']);
        $g->get('/', [App\Controllers\Admin\DashboardController::class, 'index']);

        // Hizmetler
        $g->get('/hizmetler', [App\Controllers\Admin\ServiceController::class, 'index']);
        $g->get('/hizmetler/yeni', [App\Controllers\Admin\ServiceController::class, 'create']);
        $g->post('/hizmetler', [App\Controllers\Admin\ServiceController::class, 'store']);
        $g->get('/hizmetler/{id}/duzenle', [App\Controllers\Admin\ServiceController::class, 'edit']);
        $g->post('/hizmetler/{id}', [App\Controllers\Admin\ServiceController::class, 'update']);
        $g->post('/hizmetler/{id}/sil', [App\Controllers\Admin\ServiceController::class, 'delete']);

        // İlçeler
        $g->get('/ilceler', [App\Controllers\Admin\DistrictController::class, 'index']);
        $g->get('/ilceler/yeni', [App\Controllers\Admin\DistrictController::class, 'create']);
        $g->post('/ilceler', [App\Controllers\Admin\DistrictController::class, 'store']);
        $g->get('/ilceler/{id}/duzenle', [App\Controllers\Admin\DistrictController::class, 'edit']);
        $g->post('/ilceler/{id}', [App\Controllers\Admin\DistrictController::class, 'update']);
        $g->post('/ilceler/{id}/sil', [App\Controllers\Admin\DistrictController::class, 'delete']);

        // Sayfalar
        $g->get('/sayfalar', [App\Controllers\Admin\PageController::class, 'index']);
        $g->get('/sayfalar/yeni', [App\Controllers\Admin\PageController::class, 'create']);
        $g->post('/sayfalar', [App\Controllers\Admin\PageController::class, 'store']);
        $g->get('/sayfalar/{id}/duzenle', [App\Controllers\Admin\PageController::class, 'edit']);
        $g->post('/sayfalar/{id}', [App\Controllers\Admin\PageController::class, 'update']);
        $g->post('/sayfalar/{id}/sil', [App\Controllers\Admin\PageController::class, 'delete']);

        // SSS
        $g->get('/sss', [App\Controllers\Admin\FaqController::class, 'index']);
        $g->get('/sss/yeni', [App\Controllers\Admin\FaqController::class, 'create']);
        $g->post('/sss', [App\Controllers\Admin\FaqController::class, 'store']);
        $g->get('/sss/{id}/duzenle', [App\Controllers\Admin\FaqController::class, 'edit']);
        $g->post('/sss/{id}', [App\Controllers\Admin\FaqController::class, 'update']);
        $g->post('/sss/{id}/sil', [App\Controllers\Admin\FaqController::class, 'delete']);

        // Galeri
        $g->get('/galeri', [App\Controllers\Admin\GalleryController::class, 'index']);
        $g->post('/galeri', [App\Controllers\Admin\GalleryController::class, 'store']);
        $g->post('/galeri/{id}/sil', [App\Controllers\Admin\GalleryController::class, 'delete']);

        // Mesajlar
        $g->get('/mesajlar', [App\Controllers\Admin\MessageController::class, 'index']);
        $g->get('/mesajlar/{id}', [App\Controllers\Admin\MessageController::class, 'show']);
        $g->post('/mesajlar/{id}/sil', [App\Controllers\Admin\MessageController::class, 'delete']);

        // Ayarlar & Hesap
        $g->get('/ayarlar', [App\Controllers\Admin\SettingController::class, 'edit']);
        $g->post('/ayarlar', [App\Controllers\Admin\SettingController::class, 'update']);
        $g->get('/hesap', [App\Controllers\Admin\AccountController::class, 'edit']);
        $g->post('/hesap/sifre', [App\Controllers\Admin\AccountController::class, 'updatePassword']);
    })->add(AuthMiddleware::class);
};
