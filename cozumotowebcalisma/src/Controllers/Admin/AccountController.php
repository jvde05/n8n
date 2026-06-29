<?php

declare(strict_types=1);

namespace App\Controllers\Admin;

use App\Controllers\BaseController;
use App\Repository\UserRepository;
use App\Support\Session;
use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;
use Slim\Views\Twig;

final class AccountController extends BaseController
{
    public function __construct(Twig $view, private readonly UserRepository $users)
    {
        parent::__construct($view);
    }

    public function edit(Request $request, Response $response): Response
    {
        return $this->render($response, 'admin/account.twig');
    }

    public function updatePassword(Request $request, Response $response): Response
    {
        $data    = (array) $request->getParsedBody();
        $current = (string) ($data['current_password'] ?? '');
        $new     = (string) ($data['new_password'] ?? '');
        $confirm = (string) ($data['new_password_confirm'] ?? '');

        $userId = (int) Session::get('user_id');
        $user   = $this->users->find($userId);

        if ($user === null || !password_verify($current, $user['password_hash'])) {
            Session::flash('error', 'Mevcut şifre hatalı.');
            return $this->redirect($response, '/yonetim/hesap');
        }
        if (strlen($new) < 8) {
            Session::flash('error', 'Yeni şifre en az 8 karakter olmalı.');
            return $this->redirect($response, '/yonetim/hesap');
        }
        if ($new !== $confirm) {
            Session::flash('error', 'Yeni şifreler eşleşmiyor.');
            return $this->redirect($response, '/yonetim/hesap');
        }

        $this->users->updatePassword($userId, $new);
        Session::flash('success', 'Şifreniz güncellendi.');
        return $this->redirect($response, '/yonetim/hesap');
    }
}
