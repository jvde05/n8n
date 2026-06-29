<?php

declare(strict_types=1);

namespace App\Controllers;

use App\Repository\DistrictRepository;
use App\Repository\FaqRepository;
use App\Repository\ServiceDistrictRepository;
use App\Repository\ServiceRepository;
use App\Support\LandingBuilder;
use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;
use Slim\Exception\HttpNotFoundException;
use Slim\Views\Twig;

final class ServiceController extends BaseController
{
    public function __construct(
        Twig $view,
        private readonly ServiceRepository $services,
        private readonly DistrictRepository $districts,
        private readonly ServiceDistrictRepository $serviceDistricts,
        private readonly FaqRepository $faqs,
        private readonly LandingBuilder $landing
    ) {
        parent::__construct($view);
    }

    public function index(Request $request, Response $response): Response
    {
        return $this->render($response, 'services.twig', [
            'services' => $this->services->allActive(),
        ]);
    }

    public function show(Request $request, Response $response, array $args): Response
    {
        $service = $this->services->findBySlug($args['slug']);
        if ($service === null) {
            throw new HttpNotFoundException($request);
        }

        $districts = ((int) $service['enable_districts'] === 1)
            ? $this->districts->allActive()
            : [];

        return $this->render($response, 'service.twig', [
            'service'   => $service,
            'districts' => $districts,
            'faqs'      => $this->faqs->forService((int) $service['id']),
        ]);
    }

    public function showDistrict(Request $request, Response $response, array $args): Response
    {
        $service  = $this->services->findBySlug($args['slug']);
        $district = $this->districts->findBySlug($args['district']);

        if ($service === null || $district === null || (int) $service['enable_districts'] !== 1) {
            throw new HttpNotFoundException($request);
        }

        $override = $this->serviceDistricts->findPair((int) $service['id'], (int) $district['id']);

        $body       = $override['body'] ?? null;
        $metaTitle  = $override['meta_title'] ?? null;
        $metaDesc   = $override['meta_description'] ?? null;

        return $this->render($response, 'service_district.twig', [
            'service'     => $service,
            'district'    => $district,
            'heading'     => $this->landing->heading($service, $district),
            'body'        => $body !== null && $body !== '' ? $body : $this->landing->body($service, $district),
            'meta_title'  => $metaTitle ?: $this->landing->metaTitle($service, $district),
            'meta_desc'   => $metaDesc ?: $this->landing->metaDescription($service, $district),
            'districts'   => $this->districts->allActive(),
            'faqs'        => $this->faqs->forService((int) $service['id']),
        ]);
    }
}
