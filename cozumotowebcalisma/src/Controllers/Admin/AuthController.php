<?php

declare(strict_types=1);

namespace App\Controllers\Admin;

use App\Controllers\BaseController;
use App\Repository\UserRepository;
use App\Support\Session;
use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;
use Slim\Views\Twig;

final class AuthController extends BaseController
{
    public function __construct(Twig $view, private readonly UserRepository $users)
    {
        parent::__construct($view);
    }

    public function showLogin(Request $request, Response $response): Response
    {
        if (Session::isAuthenticated()) {
            return $this->redirect($response, '/yonetim');
        }
        return $this->render($response, 'admin/login.twig', ['layout_minimal' => true]);
    }

    public function login(Request $request, Response $response): Response
    {
        $data  = (array) $request->getParsedBody();
        $email = trim((string) ($data['email'] ?? ''));
        $pass  = (string) ($data['password'] ?? '');

        $user = $this->users->findByEmail($email);

        if ($user === null || !password_verify($pass, $user['password_hash'])) {
            Session::flash('error', 'E-posta veya şifre hatalı.');
            return $this->redirect($response, '/yonetim/giris');
        }

        Session::regenerate();
        Session::set('user_id', (int) $user['id']);
        Session::set('user', [
            'id'    => (int) $user['id'],
            'name'  => $user['name'],
            'email' => $user['email'],
            'role'  => $user['role'],
        ]);
        Session::flash('success', 'Hoş geldiniz, ' . $user['name'] . '.');

        return $this->redirect($response, '/yonetim');
    }

    public function logout(Request $request, Response $response): Response
    {
        Session::destroy();
        return $this->redirect($response, '/yonetim/giris');
    }
}
