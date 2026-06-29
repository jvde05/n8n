<?php

declare(strict_types=1);

namespace App\Controllers\Admin;

use App\Controllers\BaseController;
use App\Repository\ServiceRepository;
use App\Support\Session;
use App\Support\Str;
use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;
use Slim\Exception\HttpNotFoundException;
use Slim\Views\Twig;

final class ServiceController extends BaseController
{
    public function __construct(Twig $view, private readonly ServiceRepository $services)
    {
        parent::__construct($view);
    }

    public function index(Request $request, Response $response): Response
    {
        return $this->render($response, 'admin/services/index.twig', [
            'services' => $this->services->all(),
        ]);
    }

    public function create(Request $request, Response $response): Response
    {
        return $this->render($response, 'admin/services/form.twig', [
            'service' => null,
            'action'  => '/yonetim/hizmetler',
        ]);
    }

    public function store(Request $request, Response $response): Response
    {
        $data = $this->validated((array) $request->getParsedBody());
        if ($data === null) {
            return $this->redirect($response, '/yonetim/hizmetler/yeni');
        }
        $this->services->create($data);
        Session::flash('success', 'Hizmet eklendi.');
        return $this->redirect($response, '/yonetim/hizmetler');
    }

    public function edit(Request $request, Response $response, array $args): Response
    {
        $service = $this->services->find((int) $args['id']);
        if ($service === null) {
            throw new HttpNotFoundException($request);
        }
        return $this->render($response, 'admin/services/form.twig', [
            'service' => $service,
            'action'  => '/yonetim/hizmetler/' . $service['id'],
        ]);
    }

    public function update(Request $request, Response $response, array $args): Response
    {
        $id = (int) $args['id'];
        if ($this->services->find($id) === null) {
            throw new HttpNotFoundException($request);
        }
        $data = $this->validated((array) $request->getParsedBody());
        if ($data === null) {
            return $this->redirect($response, '/yonetim/hizmetler/' . $id . '/duzenle');
        }
        $this->services->update($id, $data);
        Session::flash('success', 'Hizmet güncellendi.');
        return $this->redirect($response, '/yonetim/hizmetler');
    }

    public function delete(Request $request, Response $response, array $args): Response
    {
        $this->services->delete((int) $args['id']);
        Session::flash('success', 'Hizmet silindi.');
        return $this->redirect($response, '/yonetim/hizmetler');
    }

    private function validated(array $d): ?array
    {
        $title = trim((string) ($d['title'] ?? ''));
        if ($title === '') {
            Session::flash('error', 'Hizmet başlığı zorunludur.');
            return null;
        }
        $slug = trim((string) ($d['slug'] ?? '')) ?: $title;

        return [
            'title'            => $title,
            'slug'             => Str::slug($slug),
            'summary'          => trim((string) ($d['summary'] ?? '')) ?: null,
            'body'             => (string) ($d['body'] ?? ''),
            'icon'             => trim((string) ($d['icon'] ?? '')) ?: null,
            'image'            => trim((string) ($d['image'] ?? '')) ?: null,
            'meta_title'       => trim((string) ($d['meta_title'] ?? '')) ?: null,
            'meta_description' => trim((string) ($d['meta_description'] ?? '')) ?: null,
            'sort_order'       => (int) ($d['sort_order'] ?? 0),
            'is_active'        => isset($d['is_active']) ? 1 : 0,
            'enable_districts' => isset($d['enable_districts']) ? 1 : 0,
        ];
    }
}
