#!/bin/bash

/tmp/wait-for-it.sh db:3306

cd /var/www/search_engine
composer install
php index.php &

cd /var/www
composer install
php artisan migrate
php-fpm
