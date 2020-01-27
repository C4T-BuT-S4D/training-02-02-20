import asyncio
import secrets
import uuid
import ujson

from sanic import Sanic
from sanic.response import json
from sanic.exceptions import NotFound
from sanic.websocket import WebSocketProtocol
from aioredis.pubsub import Receiver
from functools import wraps

import storage
import exceptions

app = Sanic('collacode')


@app.exception(NotFound)
async def ignore_404s(request, _exception):
    return json({"error": f'{request.path} not found'}, status=404)


def login_required(f):
    @wraps(f)
    async def wrapper(request, *args, **kwargs):
        loop = asyncio.get_event_loop()
        redis = await storage.get_async_redis_pool(loop)

        session = request.cookies.get('session')
        is_authorized = session and redis.exists(session)

        if is_authorized:
            response = await f(request, *args, **kwargs)
            return response
        else:
            return json({'status': 'not_authorized'}, 403)

    return wrapper


async def get_code_websocket_handler(token):
    loop = asyncio.get_event_loop()
    redis = await storage.get_async_redis_pool(loop)

    async def in_handler(ws):
        while True:
            data = await ws.recv()
            data = data.encode()
            cur_data = await redis.get(token) or b''
            cur_data += data
            if len(cur_data) > 32768:
                await ws.send({'error': 'code too long'})
                continue

            await redis.set(token, cur_data, expire=1800)
            await redis.publish(f'updates:{token}', data)

    async def out_handler(ws):
        mpsc = Receiver(loop=loop)
        await redis.subscribe(mpsc.channel(f'updates:{token}'))
        async for channel, msg in mpsc.iter():
            await ws.send(msg)

    async def handler(_request, ws):
        in_task = asyncio.create_task(in_handler(ws))
        out_task = asyncio.create_task(out_handler(ws))
        await in_task
        await out_task

    return handler


@app.route('/register/', methods=['POST'])
async def register(request):
    username = request.json.get('username')
    password = request.json.get('password')
    if not username or not password:
        return json({'error': 'fill all fields'})
    if len(username) < 5:
        return json({'error': 'too short username'})

    loop = asyncio.get_event_loop()
    redis = await storage.get_async_redis_pool(loop)
    try:
        await storage.add_user(redis, username, password)
    except exceptions.UserExistsException:
        return json({'error': 'username taken'})

    return json({'status': 'ok'})


@app.route('/login/', methods=['POST'])
async def login(request):
    username = request.json.get('username')
    password = request.json.get('password')
    if not username or not password:
        return json({'error': 'fill all fields'})

    loop = asyncio.get_event_loop()
    redis = await storage.get_async_redis_pool(loop)
    user = await storage.get_user(redis, username)
    if not user:
        return json({'error': 'invalid credentials'})
    if user.get('password', '') != password:
        return json({'error': 'invalid credentials'})

    session = secrets.token_hex(30)
    await storage.set_session(redis, session, user)

    response = json({'status': 'ok'})
    response.cookies['session'] = session
    response.cookies['session']['httponly'] = True
    return response


@app.route('/logout/')
async def logout(_request):
    response = json({'status': 'ok'})
    del response.cookies['session']
    return response


@app.route('/me/')
@login_required
async def me(request):
    loop = asyncio.get_event_loop()
    redis = await storage.get_async_redis_pool(loop)
    session = request.cookies['session']
    user_data = await redis.get(session)
    return json(ujson.loads(user_data))


@app.route('/new_collab/')
@login_required
async def new_collab(_request):
    token = str(uuid.uuid4())
    handler = await get_code_websocket_handler(token)
    app.add_websocket_route(handler, f'/code/{token}')
    return json({'token': token})


# noinspection PyUnresolvedReferences
@app.route('/get_collab/<token>/')
@login_required
async def get_collab(_request, token):
    loop = asyncio.get_event_loop()
    redis = await storage.get_async_redis_pool(loop)

    data = await redis.get(token)
    return json({'data': data})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9997, protocol=WebSocketProtocol)
