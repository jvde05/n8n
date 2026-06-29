<?php

declare(strict_types=1);

namespace App\Controllers\Admin;

use App\Controllers\BaseController;
use App\Repository\DistrictRepository;
use App\Support\Session;
use App\Support\Str;
use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;
use Slim\Exception\HttpNotFoundException;
use Slim\Views\Twig;

final class DistrictController extends BaseController
{
    public function __construct(Twig $view, private readonly DistrictRepository $districts)
    {
        parent::__construct($view);
    }

    public function index(Request $request, Response $response): Response
    {
        return $this->render($response, 'admin/districts/index.twig', [
            'districts' => $this->districts->all(),
        ]);
    }

    public function create(Request $request, Response $response): Response
    {
        return $this->render($response, 'admin/districts/form.twig', [
            'district' => null,
            'action'   => '/yonetim/ilceler',
        ]);
    }

    public function store(Request $request, Response $response): Response
    {
        $data = $this->validated((array) $request->getParsedBody());
        if ($data === null) {
            return $this->redirect($response, '/yonetim/ilceler/yeni');
        }
        $this->districts->create($data);
        Session::flash('success', 'İlçe eklendi. İlgili landing sayfaları otomatik oluştu.');
        return $this->redirect($response, '/yonetim/ilceler');
    }

    public function edit(Request $request, Response $response, array $args): Response
    {
        $district = $this->districts->find((int) $args['id']);
        if ($district === null) {
            throw new HttpNotFoundException($request);
        }
        return $this->render($response, 'admin/districts/form.twig', [
            'district' => $district,
            'action'   => '/yonetim/ilceler/' . $district['id'],
        ]);
    }

    public function update(Request $request, Response $response, array $args): Response
    {
        $id = (int) $args['id'];
        if ($this->districts->find($id) === null) {
            throw new HttpNotFoundException($request);
        }
        $data = $this->validated((array) $request->getParsedBody());
        if ($data === null) {
            return $this->redirect($response, '/yonetim/ilceler/' . $id . '/duzenle');
        }
        $this->districts->update($id, $data);
        Session::flash('success', 'İlçe güncellendi.');
        return $this->redirect($response, '/yonetim/ilceler');
    }

    public function delete(Request $request, Response $response, array $args): Response
    {
        $this->districts->delete((int) $args['id']);
        Session::flash('success', 'İlçe silindi.');
        return $this->redirect($response, '/yonetim/ilceler');
    }

    private function validated(array $d): ?array
    {
        $name = trim((string) ($d['name'] ?? ''));
        if ($name === '') {
            Session::flash('error', 'İlçe adı zorunludur.');
            return null;
        }
        $slug = trim((string) ($d['slug'] ?? '')) ?: $name;

        return [
            'name'       => $name,
            'slug'       => Str::slug($slug),
            'sort_order' => (int) ($d['sort_order'] ?? 0),
            'is_active'  => isset($d['is_active']) ? 1 : 0,
        ];
    }
}
