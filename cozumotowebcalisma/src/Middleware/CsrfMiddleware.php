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
 * Tüm POST/PUT/DELETE isteklerinde CSRF token doğrular.
 */
final class CsrfMiddleware implements MiddlewareInterface
{
    private const PROTECTED = ['POST', 'PUT', 'PATCH', 'DELETE'];

    public function process(Request $request, Handler $handler): ResponseInterface
    {
        if (in_array(strtoupper($request->getMethod()), self::PROTECTED, true)) {
            $data  = (array) $request->getParsedBody();
            $token = $data['_csrf'] ?? $request->getHeaderLine('X-CSRF-Token');

            if (!Session::verifyCsrf(is_string($token) ? $token : null)) {
                Session::flash('error', 'Oturum süreniz doldu veya güvenlik doğrulaması başarısız. Lütfen tekrar deneyin.');
                $referer = $request->getHeaderLine('Referer') ?: '/';
                return (new Response())->withHeader('Location', $referer)->withStatus(302);
            }
        }

        return $handler->handle($request);
    }
}
