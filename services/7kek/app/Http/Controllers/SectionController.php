<?php

namespace App\Http\Controllers;

use App\Post;
use App\Section;
use App\User;
use Illuminate\Http\Request;

class SectionController extends Controller
{
    public function get() {
        return [
            "status" => "ok",
            "sections" => Section::query()->orderBy("id", "desc")->with("owner")
                ->simplePaginate(30, ['*'], 'page', request("page"))->items()
        ];
    }

    public function create() {
        $this->validate([
            "title" => "string|required",
            "description" => "string|nullable",
            "is_private" => "boolean|required"
        ]);

        if(Section::query()->where("title", request("title"))->exists()) {
            return [
                "status" => "failed",
                "reason" => "section_exists"
            ];
        }

        /** @var Section $section */
        $section = Section::create([
            "title" => request("title"),
            "description" => request("description"),
            "is_private" => request("is_private"),
            "owner_id" => auth()->id()
        ]);

        $section->users()->attach(auth()->user());

        return [
            "status" => "ok",
            "section" => $section
        ];
    }

    public function getPosts(Section $section) {
        if($section->isPrivate) {
            if(!auth()->check() || is_null(auth()->user()->sections->where("id", $section->id)->first()))
                return [
                    "status" => "failed",
                    "reason" => "private_section"
                ];
        }

        $posts = $section->posts()->orderBy("created_at", "desc")
            ->simplePaginate(10, ['*'], 'page', request("page"))->items();

        return [
            "status" => "ok",
            "posts" => $posts,
        ];
    }

    public function invite(Section $section) {
        $this->validate([
            "whom" => "required|exists:users,users.id"
        ]);

        if(request("whom") == auth()->id()) {
            return [
                "status" => "failed",
                "reason" => "stop_right_there_criminal_scum"
            ];
        }

        if(!$section->users()->where("users.id", auth()->id())->first()) {
            return [
                "status" => "failed",
                "reason" => "no_rights"
            ];
        }

        $section->users()->attach(User::findOrFail(request("whom")));

        return [
            "status" => "ok",
            "section" => $section->fresh()->load("users")
        ];
    }
}
