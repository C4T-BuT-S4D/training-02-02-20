<?php

namespace Tests\Feature;

use App\Section;
use App\User;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Foundation\Testing\WithFaker;
use Tests\TestCase;

class PrivacyTest extends TestCase
{
    public function testPrivateSectionPostsArentDisplayed()
    {
        $section = Section::create([
            "title" => "shit",
            "description" => "gigashit",
            "is_private" => true
        ]);

        $section->posts()->create([
            "title" => "Look at my fucking cat",
            "description" => "My cat is so amazing",
            "type" => "image",
            "src" => "https://media.moddb.com/cache/images/members/1/284/283202/thumb_620x2000/Bloodsucker.jpg"
        ]);

        $results = $this->get("/api/posts")->json();
        $this->assertCount(0, $results["posts"]);

        $user = factory(User::class)->create();
        $this->be($user);
        $user->sections()->attach($section);

        $results = $this->get("/api/posts")->json();
        $this->assertCount(1, $results["posts"]);
    }
}
