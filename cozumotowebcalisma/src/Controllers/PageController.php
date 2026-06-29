<?php

declare(strict_types=1);

namespace App\Controllers;

use App\Repository\PageRepository;
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

    public function show(Request $request, Response $response, array $args): Response
    {
        $page = $this->pages->findBySlug($args['slug']);
        if ($page === null) {
            throw new HttpNotFoundException($request);
        }

        return $this->render($response, 'page.twig', ['page' => $page]);
    }
}
