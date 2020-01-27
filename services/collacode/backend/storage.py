import ujson
import aioredis

import exceptions

_async_redis_pool = None


async def get_async_redis_pool(loop):
    global _async_redis_pool

    if not _async_redis_pool:
        address = f'redis://redis:6379'
        db = 1
        _async_redis_pool = await aioredis.create_redis_pool(
            address=address,
            db=db,
            minsize=5,
            maxsize=15,
            loop=loop,
        )

    return _async_redis_pool


async def add_user(redis, username, password):
    tr = redis.multi_exec()
    exists = tr.exists(f'user:{username}')

    username = username.strip()
    data = {
        'username': username,
        'password': password,
    }
    tr.set(f'user:{username}', ujson.dumps(data))
    await tr.execute()

    exists = await exists
    if exists:
        raise exceptions.UserExistsException


async def get_user(redis, username):
    data = await redis.get(f'user:{username}')
    if not data:
        return None

    try:
        user = ujson.loads(data)
    except ValueError:
        return None
    else:
        return user


async def set_session(redis, session, user):
    data = ujson.dumps(user)
    await redis.set(session, data)
