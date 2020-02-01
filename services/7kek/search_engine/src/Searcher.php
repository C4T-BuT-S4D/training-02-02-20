<?php


namespace Search;


use Psr\Http\Message\ServerRequestInterface;

class Searcher
{
    private $storage;

    public function __construct(IndexesStorage $storage) {
        $this->storage = $storage;
    }

    public function __invoke(ServerRequestInterface $request)
    {
        $isolation = $request->getHeader("X-Isolation")[-1] ?? "";
        $searchWord = $request->getQueryParams()["q"];

        $answers = $this->storage->isolations[$isolation][$searchWord] ?? [];

        return [json_encode($answers), 200];
    }
}
