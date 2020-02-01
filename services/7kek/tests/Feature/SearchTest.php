<?php

namespace Tests\Feature;

use App\Post;
use App\Section;
use App\Services\SearchService;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Foundation\Testing\WithFaker;
use Tests\TestCase;

class SearchTest extends TestCase
{
    public function testWeCanSearch() {
        $section = Section::create([
            "title" => "some",
            "description" => "woah",
            "is_private" => false
        ]);

        $post = Post::create([
            "section_id" => $section->id,
            "title" => "smack my bitch up",
            "description" => "i'm a bad post",
            "type" => "image",
            "src" => "kek.png"
        ]);

        $searchService = new SearchService();
        $searchService->indexPost($post);

        $posts = $searchService->searchPosts("bitch", ["some", ""]);

        $this->assertEquals($posts[0]->id, $post->id);
    }
}
