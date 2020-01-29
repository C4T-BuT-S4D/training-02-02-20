<?php

namespace Tests\Feature;

use App\User;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Foundation\Testing\WithFaker;
use Tests\TestCase;

class AuthTest extends TestCase
{
    public function testRegistration()
    {
        $response = $this->post('/api/auth/register', [
            "email" => "priah@mail.ru",
            "password" => "KissMyAss"
        ])->json();

        $this->assertEquals("ok", $response["status"]);
        $this->assertNotNull($response["user"]);
    }

    public function testLogin() {
        $user = factory(User::class)->create();
        $user->save();

        $response = $this->post('/api/auth/login', [
            "email" => $user->email,
            "password" => "12345qwerty"
        ])->json();

        $this->assertEquals("ok", $response["status"]);
        $this->assertNotEmpty($response["token"]["token"]);
    }
}
