<?php


namespace App\Services;


use App\Post;
use GuzzleHttp\Client;

class SearchService
{
    public function searchPosts($word, $isolations) {
        $client = new Client();
        $postIds = [];

        foreach($isolations as $isolation) {
            $r = $client->get("http://localhost:8090/search", [
                "query" => [
                    "q" => $word,
                ],
                "headers" => [
                    "X-Isolation" => $isolation
                ]
            ])->getBody()->getContents();

            $results = json_decode($r, true);
            $postIds = array_unique(array_merge($postIds, $results));
        }

        return Post::query()->whereIn("id", $postIds)->get();
    }

    public function indexPost(Post $post) {
        $words = array_map("trim", explode(" ", $post->title));

        $isolation = ($post->section->is_private)? $post->section->title : "";

        $client = new Client();
        $client->get("http://localhost:8090/index", [
             "query" => [
                 "words" => $words,
                 "target_id" => $post->id
             ],
            "headers" => [
                "X-Isolation" => $isolation
            ]
        ]);
    }
}
