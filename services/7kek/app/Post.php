<?php

namespace App;

use Illuminate\Database\Eloquent\Model;

class Post extends Model
{
    protected $guarded = [];

    public function section() {
        return $this->belongsTo(Section::class, "section_id");
    }
}
