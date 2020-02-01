<?php

namespace App\Http\Controllers;

use App\User;
use Illuminate\Http\Request;

class LoginController extends Controller
{
    public function login() {
        /** @var User $user */
        $user = User::query()
            ->where("username", request()->post("username"))->first();

        if(!$user || ($user->password != request()->post('password')))
            return [
                "status" => "failed",
                "reason" => "bad_auth"
            ];

        $token = $user->tokens()->create([
            "token" => \Str::random(40)
        ]);

        return [
            "status" => "ok",
            "token" => $token
        ];
    }

    public function register() {
        $this->validate([
            "username" => "string|required|min:3",
            "password" => "string|required"
        ]);

        if(User::where("username", request("username"))->exists()) {
            return [
                "status" => "failed",
                "reason" => "username_taken"
            ];
        }

        $user = User::create(request()->only(["username", "password"]));

        return [
            "status" => "ok",
            "user" => $user
        ];
    }
}
