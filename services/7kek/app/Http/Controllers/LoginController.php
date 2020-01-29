<?php

namespace App\Http\Controllers;

use App\User;
use Illuminate\Http\Request;

class LoginController extends Controller
{
    public function login() {
        $this->validate([
            "email" => "email|required",
            "password" => "string|required"
        ]);

        /** @var User $user */
        $user = User::query()
            ->where("email", "like", strtolower(request("email")))->first();

        if(!$user || !\Hash::check(request('password'), $user->password))
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
            "email" => "email|required",
            "password" => "string|required"
        ]);

        if(User::where("email", request("email"))->exists()) { // First vuln
            return [
                "status" => "failed",
                "reason" => "email_taken"
            ];
        }

        $user = User::create(request(["email", "password"]));

        return [
            "status" => "ok",
            "user" => $user
        ];
    }
}
