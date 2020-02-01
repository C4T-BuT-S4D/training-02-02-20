<?php

use Search\Indexer;
use Search\Searcher;

require __DIR__ . "/vendor/autoload.php";

$loop = React\EventLoop\Factory::create();

$router = new \Search\Router();

$storage = new \Search\IndexesStorage();

$router->register("/index", new Indexer($storage));
$router->register("/search", new Searcher($storage));

$server = new React\Http\Server(function (Psr\Http\Message\ServerRequestInterface $request) use ($router) {
    list($response, $status) = $router->route($request);
    return new React\Http\Response(
        $status,
        array('Content-Type' => 'text/html'),
        $response
    );
});

$socket = new React\Socket\Server(8090, $loop);
$server->listen($socket);

echo "Server running at http://127.0.0.1:8090\n";

$loop->run();
