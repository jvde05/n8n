<?php

declare(strict_types=1);

namespace App\Controllers\Admin;

use App\Controllers\BaseController;
use App\Repository\PageRepository;
use App\Support\Session;
use App\Support\Str;
use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;
use Slim\Exception\HttpNotFoundException;
use Slim\Views\Twig;

final class PageController extends BaseController
{
    public function __construct(Twig $view, private readonly PageRepository $pages)
    {
        parent::__construct($view);
    }

    public function index(Request $request, Response $response): Response
    {
        return $this->render($response, 'admin/pages/index.twig', ['pages' => $this->pages->all()]);
    }

    public function create(Request $request, Response $response): Response
    {
        return $this->render($response, 'admin/pages/form.twig', [
            'page'   => null,
            'action' => '/yonetim/sayfalar',
        ]);
    }

    public function store(Request $request, Response $response): Response
    {
        $data = $this->validated((array) $request->getParsedBody());
        if ($data === null) {
            return $this->redirect($response, '/yonetim/sayfalar/yeni');
        }
        $this->pages->create($data);
        Session::flash('success', 'Sayfa eklendi.');
        return $this->redirect($response, '/yonetim/sayfalar');
    }

    public function edit(Request $request, Response $response, array $args): Response
    {
        $page = $this->pages->find((int) $args['id']);
        if ($page === null) {
            throw new HttpNotFoundException($request);
        }
        return $this->render($response, 'admin/pages/form.twig', [
            'page'   => $page,
            'action' => '/yonetim/sayfalar/' . $page['id'],
        ]);
    }

    public function update(Request $request, Response $response, array $args): Response
    {
        $id = (int) $args['id'];
        if ($this->pages->find($id) === null) {
            throw new HttpNotFoundException($request);
        }
        $data = $this->validated((array) $request->getParsedBody());
        if ($data === null) {
            return $this->redirect($response, '/yonetim/sayfalar/' . $id . '/duzenle');
        }
        $this->pages->update($id, $data);
        Session::flash('success', 'Sayfa güncellendi.');
        return $this->redirect($response, '/yonetim/sayfalar');
    }

    public function delete(Request $request, Response $response, array $args): Response
    {
        $this->pages->delete((int) $args['id']);
        Session::flash('success', 'Sayfa silindi.');
        return $this->redirect($response, '/yonetim/sayfalar');
    }

    private function validated(array $d): ?array
    {
        $title = trim((string) ($d['title'] ?? ''));
        if ($title === '') {
            Session::flash('error', 'Sayfa başlığı zorunludur.');
            return null;
        }
        $slug = trim((string) ($d['slug'] ?? '')) ?: $title;

        return [
            'title'            => $title,
            'slug'             => Str::slug($slug),
            'body'             => (string) ($d['body'] ?? ''),
            'meta_title'       => trim((string) ($d['meta_title'] ?? '')) ?: null,
            'meta_description' => trim((string) ($d['meta_description'] ?? '')) ?: null,
            'is_active'        => isset($d['is_active']) ? 1 : 0,
        ];
    }
}
