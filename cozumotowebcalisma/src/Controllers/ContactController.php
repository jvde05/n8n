<?php

declare(strict_types=1);

namespace App\Controllers;

use App\Repository\MessageRepository;
use App\Support\Session;
use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;
use Slim\Views\Twig;

final class ContactController extends BaseController
{
    public function __construct(Twig $view, private readonly MessageRepository $messages)
    {
        parent::__construct($view);
    }

    public function show(Request $request, Response $response): Response
    {
        return $this->render($response, 'contact.twig');
    }

    public function submit(Request $request, Response $response): Response
    {
        $data = (array) $request->getParsedBody();

        $name  = trim((string) ($data['name'] ?? ''));
        $phone = trim((string) ($data['phone'] ?? ''));
        $email = trim((string) ($data['email'] ?? ''));
        $body  = trim((string) ($data['message'] ?? ''));

        // Bal küpü alanı (spam koruması).
        if (!empty($data['website'])) {
            return $this->redirect($response, '/iletisim');
        }

        $errors = [];
        if ($name === '') {
            $errors[] = 'Ad Soyad zorunludur.';
        }
        if ($phone === '' && $email === '') {
            $errors[] = 'Telefon veya e-posta bilgisinden en az birini girin.';
        }
        if ($body === '') {
            $errors[] = 'Mesaj alanı boş bırakılamaz.';
        }
        if ($email !== '' && !filter_var($email, FILTER_VALIDATE_EMAIL)) {
            $errors[] = 'Geçerli bir e-posta adresi girin.';
        }

        if ($errors !== []) {
            foreach ($errors as $e) {
                Session::flash('error', $e);
            }
            return $this->redirect($response, '/iletisim');
        }

        $this->messages->create([
            'name'    => $name,
            'phone'   => $phone ?: null,
            'email'   => $email ?: null,
            'subject' => trim((string) ($data['subject'] ?? '')) ?: 'İletişim Formu',
            'body'    => $body,
        ]);

        Session::flash('success', 'Mesajınız bize ulaştı. En kısa sürede dönüş yapacağız.');
        return $this->redirect($response, '/iletisim');
    }
}
