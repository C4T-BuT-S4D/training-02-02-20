<?php

namespace Search;

use Psr\Http\Message\ServerRequestInterface;

class Router
{
    protected $routes;

    public function __construct() {
        $this->routes = [];
    }

    public function route(ServerRequestInterface $request) {
        $path = $request->getUri()->getPath();

        if(isset($this->routes[$path]))
            return $this->routes[$path]($request);

        return ["Not found", 404];
    }

    public function register($path, callable $callback) {
        $this->routes[$path] = $callback;
    }
}
