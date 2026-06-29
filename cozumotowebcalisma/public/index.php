<?php

declare(strict_types=1);

use App\Support\Session;
use DI\ContainerBuilder;
use Dotenv\Dotenv;
use Slim\Factory\AppFactory;
use Slim\Views\Twig;
use Slim\Views\TwigMiddleware;

require __DIR__ . '/../vendor/autoload.php';

$root = dirname(__DIR__);

// Ortam değişkenleri (.env varsa).
if (is_file($root . '/.env')) {
    Dotenv::createImmutable($root)->safeLoad();
}

// Container.
$builder = new ContainerBuilder();
$builder->addDefinitions(require $root . '/config/container.php');
$container = $builder->build();

$settings = $container->get('settings');

// Oturumu başlat.
Session::start($settings['session']['name']);

AppFactory::setContainer($container);
$app = AppFactory::create();

$app->addBodyParsingMiddleware();
$app->add(TwigMiddleware::createFromContainer($app, Twig::class));
$app->add(new App\Middleware\CsrfMiddleware());
$app->addRoutingMiddleware();

// Hata yönetimi.
$displayErrors = (bool) $settings['app']['debug'];
$errorMiddleware = $app->addErrorMiddleware($displayErrors, true, true);
$errorMiddleware->setErrorHandler(
    Slim\Exception\HttpNotFoundException::class,
    function ($request) use ($app, $container) {
        $twig = $container->get(Twig::class);
        $response = $app->getResponseFactory()->createResponse(404);
        return $twig->render($response, 'errors/404.twig', [
            'flash' => Session::takeFlash(),
            'csrf'  => Session::csrfToken(),
            'auth'  => Session::user(),
        ]);
    }
);

// Rotalar.
(require $root . '/config/routes.php')($app);

$app->run();
