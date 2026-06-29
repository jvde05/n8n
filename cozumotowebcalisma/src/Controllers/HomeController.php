<?php

declare(strict_types=1);

namespace App\Controllers;

use App\Repository\FaqRepository;
use App\Repository\GalleryRepository;
use App\Repository\ServiceRepository;
use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;
use Slim\Views\Twig;

final class HomeController extends BaseController
{
    public function __construct(
        Twig $view,
        private readonly ServiceRepository $services,
        private readonly FaqRepository $faqs,
        private readonly GalleryRepository $gallery
    ) {
        parent::__construct($view);
    }

    public function index(Request $request, Response $response): Response
    {
        return $this->render($response, 'home.twig', [
            'services' => $this->services->allActive(),
            'faqs'     => $this->faqs->general(),
            'gallery'  => array_slice($this->gallery->allActive(), 0, 8),
        ]);
    }
}
