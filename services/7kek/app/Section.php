<?php

namespace App;

use Illuminate\Database\Eloquent\Model;

class Section extends Model
{
    protected $guarded = [];

    public function posts() {
        return $this->hasMany(Post::class);
    }

    public function users() {
        return $this->belongsToMany(User::class, "user_to_section", "section_id", "user_id");
    }
}
