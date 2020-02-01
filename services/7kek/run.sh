#!/bin/bash

composer install

cd search_engine
composer install

cd ..
docker-compose up --build --force-recreate -d
