#!/bin/bash

cd /var/www/search_engine
php index.php &

cd /var/www
php artisan migrate
php-fpm
