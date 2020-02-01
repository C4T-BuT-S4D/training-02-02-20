<?php

namespace App\Http\Middleware;

use App\Token;
use Closure;

class Authenticate
{
    /**
     * Handle an incoming request.
     *
     * @param  \Illuminate\Http\Request  $request
     * @param  \Closure  $next
     * @return mixed
     */
    public function handle($request, Closure $next)
    {
        $token = $request->query("token") ?? $request->post("token") ?? null;

        if($token) {
            $tokenModel = Token::query()->where("token", $token)->first();
            if($tokenModel)
                auth()->login($tokenModel->user);
        }

        if(!auth()->id())
            abort(403);

        return $next($request);
    }
}
