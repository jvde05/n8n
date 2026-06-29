<?php

declare(strict_types=1);

namespace App\Controllers;

use App\Support\Session;
use Psr\Http\Message\ResponseInterface as Response;
use Slim\Views\Twig;

abstract class BaseController
{
    public function __construct(protected readonly Twig $view)
    {
    }

    protected function render(Response $response, string $template, array $data = []): Response
    {
        $data['flash'] = Session::takeFlash();
        $data['csrf']  = Session::csrfToken();
        $data['auth']  = Session::user();
        return $this->view->render($response, $template, $data);
    }

    protected function redirect(Response $response, string $to, int $status = 302): Response
    {
        return $response->withHeader('Location', $to)->withStatus($status);
    }
}
