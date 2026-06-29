<?php

declare(strict_types=1);

namespace App\Controllers\Admin;

use App\Controllers\BaseController;
use App\Repository\FaqRepository;
use App\Repository\ServiceRepository;
use App\Support\Session;
use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;
use Slim\Exception\HttpNotFoundException;
use Slim\Views\Twig;

final class FaqController extends BaseController
{
    public function __construct(
        Twig $view,
        private readonly FaqRepository $faqs,
        private readonly ServiceRepository $services
    ) {
        parent::__construct($view);
    }

    public function index(Request $request, Response $response): Response
    {
        return $this->render($response, 'admin/faqs/index.twig', ['faqs' => $this->faqs->all()]);
    }

    public function create(Request $request, Response $response): Response
    {
        return $this->render($response, 'admin/faqs/form.twig', [
            'faq'      => null,
            'services' => $this->services->all(),
            'action'   => '/yonetim/sss',
        ]);
    }

    public function store(Request $request, Response $response): Response
    {
        $data = $this->validated((array) $request->getParsedBody());
        if ($data === null) {
            return $this->redirect($response, '/yonetim/sss/yeni');
        }
        $this->faqs->create($data);
        Session::flash('success', 'Soru eklendi.');
        return $this->redirect($response, '/yonetim/sss');
    }

    public function edit(Request $request, Response $response, array $args): Response
    {
        $faq = $this->faqs->find((int) $args['id']);
        if ($faq === null) {
            throw new HttpNotFoundException($request);
        }
        return $this->render($response, 'admin/faqs/form.twig', [
            'faq'      => $faq,
            'services' => $this->services->all(),
            'action'   => '/yonetim/sss/' . $faq['id'],
        ]);
    }

    public function update(Request $request, Response $response, array $args): Response
    {
        $id = (int) $args['id'];
        if ($this->faqs->find($id) === null) {
            throw new HttpNotFoundException($request);
        }
        $data = $this->validated((array) $request->getParsedBody());
        if ($data === null) {
            return $this->redirect($response, '/yonetim/sss/' . $id . '/duzenle');
        }
        $this->faqs->update($id, $data);
        Session::flash('success', 'Soru güncellendi.');
        return $this->redirect($response, '/yonetim/sss');
    }

    public function delete(Request $request, Response $response, array $args): Response
    {
        $this->faqs->delete((int) $args['id']);
        Session::flash('success', 'Soru silindi.');
        return $this->redirect($response, '/yonetim/sss');
    }

    private function validated(array $d): ?array
    {
        $q = trim((string) ($d['question'] ?? ''));
        $a = trim((string) ($d['answer'] ?? ''));
        if ($q === '' || $a === '') {
            Session::flash('error', 'Soru ve cevap alanları zorunludur.');
            return null;
        }
        return [
            'service_id' => $d['service_id'] ?? null,
            'question'   => $q,
            'answer'     => $a,
            'sort_order' => (int) ($d['sort_order'] ?? 0),
            'is_active'  => isset($d['is_active']) ? 1 : 0,
        ];
    }
}
