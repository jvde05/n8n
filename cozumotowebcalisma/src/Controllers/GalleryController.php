<?php

declare(strict_types=1);

namespace App\Controllers;

use App\Repository\GalleryRepository;
use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;
use Slim\Views\Twig;

final class GalleryController extends BaseController
{
    public function __construct(Twig $view, private readonly GalleryRepository $gallery)
    {
        parent::__construct($view);
    }

    public function index(Request $request, Response $response): Response
    {
        return $this->render($response, 'gallery.twig', [
            'images' => $this->gallery->allActive(),
        ]);
    }
}
