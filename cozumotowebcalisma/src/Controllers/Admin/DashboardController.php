<?php

declare(strict_types=1);

namespace App\Controllers\Admin;

use App\Controllers\BaseController;
use App\Repository\DistrictRepository;
use App\Repository\GalleryRepository;
use App\Repository\MessageRepository;
use App\Repository\ServiceRepository;
use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;
use Slim\Views\Twig;

final class DashboardController extends BaseController
{
    public function __construct(
        Twig $view,
        private readonly ServiceRepository $services,
        private readonly DistrictRepository $districts,
        private readonly GalleryRepository $gallery,
        private readonly MessageRepository $messages
    ) {
        parent::__construct($view);
    }

    public function index(Request $request, Response $response): Response
    {
        return $this->render($response, 'admin/dashboard.twig', [
            'stats' => [
                'services'  => count($this->services->all()),
                'districts' => count($this->districts->all()),
                'gallery'   => count($this->gallery->all()),
                'unread'    => $this->messages->unreadCount(),
            ],
            'recent_messages' => array_slice($this->messages->all(), 0, 5),
        ]);
    }
}
