<?php

namespace App;

use Illuminate\Database\Eloquent\Model;

/*
 * Token for api authorization
 */
class Token extends Model
{
    protected $guarded = [];

    public function user() {
        return $this->belongsTo(User::class, "user_id");
    }
}
