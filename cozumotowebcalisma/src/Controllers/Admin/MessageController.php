<?php

declare(strict_types=1);

namespace App\Controllers\Admin;

use App\Controllers\BaseController;
use App\Repository\MessageRepository;
use App\Support\Session;
use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;
use Slim\Exception\HttpNotFoundException;
use Slim\Views\Twig;

final class MessageController extends BaseController
{
    public function __construct(Twig $view, private readonly MessageRepository $messages)
    {
        parent::__construct($view);
    }

    public function index(Request $request, Response $response): Response
    {
        return $this->render($response, 'admin/messages/index.twig', [
            'messages' => $this->messages->all(),
        ]);
    }

    public function show(Request $request, Response $response, array $args): Response
    {
        $message = $this->messages->find((int) $args['id']);
        if ($message === null) {
            throw new HttpNotFoundException($request);
        }
        if ((int) $message['is_read'] === 0) {
            $this->messages->markRead((int) $message['id']);
        }
        return $this->render($response, 'admin/messages/show.twig', ['message' => $message]);
    }

    public function delete(Request $request, Response $response, array $args): Response
    {
        $this->messages->delete((int) $args['id']);
        Session::flash('success', 'Mesaj silindi.');
        return $this->redirect($response, '/yonetim/mesajlar');
    }
}
