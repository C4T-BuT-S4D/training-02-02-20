<?php

namespace App\Http\Controllers;

use App\User;

class ProfilesController extends Controller
{
    public function get(User $user) {
        return [
            "status" => "ok",
            "user" => $user->load(["sections"])
        ];
    }
}
