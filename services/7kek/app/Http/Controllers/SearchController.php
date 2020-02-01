<?php


namespace App\Http\Controllers;


use App\Services\SearchService;

class SearchController extends Controller
{
    protected $service;

    public function __construct()
    {
        $this->service = new SearchService();
    }

    public function searchPosts() {
        $this->validate([
            "q" => "string|required"
        ]);

        $isolations = [""];

        if(auth()->check())
            foreach(auth()->user()->sections as $section) {
                $isolations[] = $section->title;
            }

        $isolations = array_unique($isolations);

        $posts = $this->service->searchPosts(request("q"), $isolations);

        return [
            "status" => "ok",
            "posts" => $posts,
            "isolations" => $isolations
        ];
    }
}
