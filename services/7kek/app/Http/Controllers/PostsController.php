<?php

namespace App\Http\Controllers;

use App\Post;
use Illuminate\Http\Request;

class PostsController extends Controller
{
    public function create() {
        $this->validate([
            "title" => "string|required|min:6",
            "description" => "string|nullable",
            "type" => "in:link,image",
            "src" => "string|required",
            "section_id" => "required|exists:sections,id"
        ]);

        /** @var Post $post */
        $post = Post::create(request()->all()); // TODO: first vulnerability

        auth()->user()->sections()->attach($post->section);

        return [
            "status" => "ok",
            "post" => $post
        ];
    }

    public function getMainPage() {
        $this->validate([
            "page" => "nullable"
        ]);

        $authorizedSections = [];
        if(auth()->id())
            $authorizedSections = auth()->user()->sections->pluck('id')->all();


        $posts = Post::query()
            ->where("sections.is_private", false)
            ->orWhereIn("sections.id", $authorizedSections)
            ->orderBy("posts.created_at", "desc")
            ->leftJoin("sections", "posts.section_id", "=", "sections.id")
            ->simplePaginate(10, ['*'], 'page', request("page") ?? 1)->items();

        return [
            "status" => "ok",
            "posts" => $posts
        ];
    }
}
