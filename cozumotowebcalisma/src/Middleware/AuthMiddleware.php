<?php

declare(strict_types=1);

namespace App\Middleware;

use App\Support\Session;
use Psr\Http\Message\ResponseInterface;
use Psr\Http\Message\ServerRequestInterface as Request;
use Psr\Http\Server\MiddlewareInterface;
use Psr\Http\Server\RequestHandlerInterface as Handler;
use Slim\Psr7\Response;

/**
 * Yönetim paneli rotalarını korur. Oturum yoksa giriş sayfasına yönlendirir.
 */
final class AuthMiddleware implements MiddlewareInterface
{
    public function process(Request $request, Handler $handler): ResponseInterface
    {
        if (!Session::isAuthenticated()) {
            Session::flash('error', 'Devam etmek için giriş yapın.');
            $response = new Response();
            return $response
                ->withHeader('Location', '/yonetim/giris')
                ->withStatus(302);
        }

        return $handler->handle($request);
    }
}
