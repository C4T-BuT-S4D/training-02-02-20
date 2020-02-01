#!/bin/bash

cd /var/www/search_engine
composer install
php index.php &

cd /var/www
composer install
php artisan migrate
php-fpm
