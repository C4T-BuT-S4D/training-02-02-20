<?php

namespace Tests\Feature;

use App\Post;
use App\Section;
use App\User;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Foundation\Testing\WithFaker;
use Tests\TestCase;

class PostsTest extends TestCase
{
    public function testPostIsCreatable()
    {
        $this->be(factory(User::class)->create());

        $results = $this->post("/api/posts", [
            "title" => "Megapost",
            "description" => "My megadescription",
            "type" => "image",
            "src" => "https://i1.sndcdn.com/artworks-000263820008-ylk79a-t500x500.jpg",
            "section_id" => (Section::create(["title" => "something", "description" => "something"]))->id
        ])->json();

        $this->assertEquals("ok", $results["status"]);
        $this->assertDatabaseHas("posts", [
            "title" => "Megapost"
        ]);
    }

    public function testWeCanSeePosts() {
        Post::create([
            "title" => "WOW",
            "description" => "WOWOWOW",
            "type" => "image",
            "src" => "https://i1.sndcdn.com/artworks-000263820008-ylk79a-t500x500.jpg",
            "section_id" => (Section::create(["title" => "none", "is_private" => false]))->id
        ]);

        $results = $this->get("/api/posts")->json();
        $this->assertEquals("ok", $results["status"]);
        $this->assertCount(1, $results["posts"]);
    }

    public function testWeCanSeePostsInSection() {
        $section = Section::create(["title" => "none", "is_private" => true]);

        Post::create([
            "title" => "WOW",
            "description" => "WOWOWOW",
            "type" => "image",
            "src" => "https://i1.sndcdn.com/artworks-000263820008-ylk79a-t500x500.jpg",
            "section_id" => $section->id
        ]);

        $results = $this->get("/api/sections/{$section->id}/posts")->json();
        $this->assertEquals("ok", $results["status"]);
        $this->assertCount(1, $results["posts"]);
    }
}
