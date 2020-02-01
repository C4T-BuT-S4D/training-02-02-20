<?php

namespace Tests\Feature;

use App\Section;
use App\User;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Foundation\Testing\WithFaker;
use Tests\TestCase;

class SectionsTest extends TestCase
{
    public function testWeCanGetAllSections() {
        Section::create([
            "title" => "shit",
            "description" => "gigashit",
            "is_private" => true
        ]);

        $results = $this->get("/api/sections")->json();

        $this->assertEquals("ok", $results["status"]);
        $this->assertCount(1, $results["sections"]);
    }

    public function testWeCanCreateASection() {
        $this->be(factory(User::class)->create());

        $results = $this->post("/api/sections", [
            "title" => "strawberry",
            "description" => "what else do you want?",
            "is_private" => true
        ])->json();

        $this->assertEquals("ok", $results["status"]);
        $this->assertEquals(true, $results["section"]["is_private"]);
    }

    public function testWeCanInvite() {
        $me = factory(User::class)->create();
        $friend = factory(User::class)->create();

        $this->be($me);

        $section = Section::create([
            "owner_id" => $me->id,
            "title" => "shit"
        ]);
        $section->users()->attach($me);

        $results = $this->post("/api/sections/{$section->id}/invite", [
            "whom" => $friend->id
        ])->json();

        $this->assertEquals("ok", $results["status"]);
        $this->assertDatabaseHas("user_to_section", [
            "user_id" => $friend->id,
            "section_id" => $section->id
        ]);
    }
}
