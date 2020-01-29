<?php

use App\Http\Middleware\Authenticate;
use Illuminate\Http\Request;

/*
|--------------------------------------------------------------------------
| API Routes
|--------------------------------------------------------------------------
|
| Here is where you can register API routes for your application. These
| routes are loaded by the RouteServiceProvider within a group which
| is assigned the "api" middleware group. Enjoy building your API!
|
*/

Route::middleware('auth:api')->get('/user', function (Request $request) {
    return $request->user();
});

Route::group(["middleware" => Authenticate::class], function() {
    Route::post("/posts", "PostsController@create");

    Route::post("/sections", "SectionController@create");
    Route::post("/sections/{section}/invite", "SectionController@invite");
});

Route::post("/auth/login", "LoginController@login");
Route::post("/auth/register", "LoginController@register");

Route::get("/sections/{section}/posts", "SectionController@getPosts");
Route::get("/sections", "SectionController@get");

Route::get("/posts", "PostsController@getMainPage");

Route::get("/profiles/{user}", "ProfilesController@get");

Route::get("/search", "SearchController@searchPosts");
