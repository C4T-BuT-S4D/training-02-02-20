<?php

namespace Tests\Feature;

use App\Section;
use App\User;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Foundation\Testing\WithFaker;
use Tests\TestCase;

class ProfilesTest extends TestCase
{
    public function testWeCanGetAProfile() {
        $user = factory(User::class)->create();
        $user->sections()->attach(Section::create([
            "title" => "kek",
            "description" => "lol"
        ]));

        $this->be($user);

        $results = $this->get("/api/profiles/{$user->id}")->json();

        $this->assertEquals("ok", $results["status"]);
        $this->assertEquals($user->email, $results["user"]["email"]);
        $this->assertCount(1, $results["user"]["sections"]);
    }
}
