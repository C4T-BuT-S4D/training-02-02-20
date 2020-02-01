<?php


namespace Search;


use Psr\Http\Message\ServerRequestInterface;

class Indexer
{
    private $storage;

    public function __construct(IndexesStorage $storage) {
        $this->storage = $storage;
    }

    public function __invoke(ServerRequestInterface $request) {
        $isolation = $request->getHeader("X-Isolation")[-1] ?? "";

        if (!isset($this->storage->isolations[$isolation]))
            $this->storage->isolations[$isolation] = [];

        $words = $request->getQueryParams()["words"] ?? [];
        $target_id = $request->getQueryParams()["target_id"] ?? 0;


        foreach($words as $word) {
            $this->storage->isolations[$isolation][$word][] = $target_id;
            $this->storage->isolations[$isolation][$word] = array_unique($this->storage->isolations[$isolation][$word]);
        }

        return ["ok", 200];
    }
}
