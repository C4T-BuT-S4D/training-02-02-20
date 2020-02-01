import uuid

import aioredis
import ujson

import exceptions


async def get_async_redis(loop):
    address = f'redis://redis:6379'
    db = 1
    return await aioredis.create_redis(
        address=address,
        db=db,
        loop=loop,
    )


async def add_user(redis, username, password):
    tr = redis.multi_exec()
    exists = tr.exists(f'user:{username}')

    username = username.strip()
    data = {
        'username': username,
        'password': password,
    }
    tr.set(f'user:{username}', ujson.dumps(data))
    tr.lpush('users', username)
    await tr.execute()

    exists = await exists
    if exists:
        raise exceptions.UserExistsException


async def get_users_listing(redis, limit, offset):
    tr = redis.multi_exec()
    cnt = tr.llen('users')
    users = tr.lrange('users', offset, offset + limit - 1)
    await tr.execute()

    data = {
        'count': await cnt,
        'users': await users,
    }

    return data


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


async def get_users_collabs(redis, username):
    return await redis.smembers(f'user:{username}:collabs')


async def get_current_user(redis, request):
    session = request.cookies['session']
    user_data = await redis.get(session)
    if not user_data:
        return None
    return ujson.loads(user_data)


async def set_session(redis, session, user):
    data = ujson.dumps(user)
    await redis.set(session, data)


async def add_collab(redis, request):
    token = str(uuid.uuid4())

    f = request.json.get('format', 'json')
    user = await get_current_user(redis, request)
    username = user['username']

    await redis.set(f"code:{token}:format", f)
    await redis.sadd(f'user:{username}:collabs', token)

    return token
