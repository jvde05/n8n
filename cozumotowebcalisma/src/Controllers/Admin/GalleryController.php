<?php

declare(strict_types=1);

namespace App\Controllers\Admin;

use App\Controllers\BaseController;
use App\Repository\GalleryRepository;
use App\Support\Session;
use App\Support\Str;
use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;
use Psr\Http\Message\UploadedFileInterface;
use Slim\Views\Twig;

final class GalleryController extends BaseController
{
    private const ALLOWED = ['image/jpeg' => 'jpg', 'image/png' => 'png', 'image/webp' => 'webp', 'image/gif' => 'gif'];

    public function __construct(
        Twig $view,
        private readonly GalleryRepository $gallery,
        private readonly string $uploadDir
    ) {
        parent::__construct($view);
    }

    public function index(Request $request, Response $response): Response
    {
        return $this->render($response, 'admin/gallery/index.twig', [
            'images' => $this->gallery->all(),
        ]);
    }

    public function store(Request $request, Response $response): Response
    {
        $files = $request->getUploadedFiles();
        $body  = (array) $request->getParsedBody();

        /** @var UploadedFileInterface[] $images */
        $images = $files['images'] ?? [];
        if ($images instanceof UploadedFileInterface) {
            $images = [$images];
        }

        $count = 0;
        foreach ($images as $image) {
            if ($image->getError() !== UPLOAD_ERR_OK) {
                continue;
            }
            $mime = $image->getClientMediaType();
            if (!isset(self::ALLOWED[$mime])) {
                Session::flash('error', 'Desteklenmeyen dosya türü: ' . $mime);
                continue;
            }
            if ($image->getSize() > 8 * 1024 * 1024) {
                Session::flash('error', 'Dosya boyutu 8MB sınırını aşıyor.');
                continue;
            }

            $ext  = self::ALLOWED[$mime];
            $name = date('Ymd-His') . '-' . bin2hex(random_bytes(4)) . '.' . $ext;
            $image->moveTo($this->uploadDir . '/' . $name);

            $this->gallery->create([
                'title'      => trim((string) ($body['title'] ?? '')) ?: null,
                'file_path'  => 'assets/uploads/' . $name,
                'sort_order' => (int) ($body['sort_order'] ?? 0),
                'is_active'  => 1,
            ]);
            $count++;
        }

        Session::flash($count > 0 ? 'success' : 'error', $count > 0 ? "$count görsel yüklendi." : 'Hiç görsel yüklenmedi.');
        return $this->redirect($response, '/yonetim/galeri');
    }

    public function delete(Request $request, Response $response, array $args): Response
    {
        $image = $this->gallery->find((int) $args['id']);
        if ($image !== null) {
            $path = dirname($this->uploadDir, 2) . '/public/' . $image['file_path'];
            // Yol public/assets/uploads altında ise dosyayı da sil.
            $full = $this->publicPath($image['file_path']);
            if ($full !== null && is_file($full)) {
                @unlink($full);
            }
            $this->gallery->delete((int) $args['id']);
            Session::flash('success', 'Görsel silindi.');
        }
        return $this->redirect($response, '/yonetim/galeri');
    }

    private function publicPath(string $relative): ?string
    {
        $publicRoot = dirname($this->uploadDir, 2); // .../public
        $candidate  = $publicRoot . '/' . ltrim($relative, '/');
        $real       = realpath($candidate);
        return ($real !== false && str_starts_with($real, realpath($publicRoot) ?: $publicRoot)) ? $real : null;
    }
}
