# 7kek

It's an API written in Laravel, allowing users to share funny pictures and useful links.

Posts are split into sections which can be made private; users having access to a section can invite other users.

You can even search posts! ...One word a time, though.

## Tech stuff

If you start a service first time and get a bunch of 502s — check your logs. Probably composer is still getting dependencies loaded!

If you experience performance issues, check your docker-compose.yml — it mounts code (especially /vendor) as a volume, which is useful (you don't have to rebuild container when code changes), but it slows things down quite a bit.

