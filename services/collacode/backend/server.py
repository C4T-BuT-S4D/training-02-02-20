import asyncio
import secrets
from functools import wraps

import ujson
from aioredis.pubsub import Receiver
from diff_match_patch import diff_match_patch
from sanic import Sanic
from sanic.exceptions import NotFound
from sanic.response import json
from sanic.websocket import WebSocketProtocol
from sanic_cors import CORS

import exceptions
import storage

app = Sanic('collacode')
CORS(app,
    resources={r"/api/*": {"origins": "http://127.0.0.1:8080"}},
    supports_credentials=True,
    automatic_options=True,
)


@app.exception(NotFound)
async def ignore_404s(request, _exception):
    return json({"error": f'{request.path} not found'}, status=404)


def login_required(f):
    @wraps(f)
    async def wrapper(request, *args, **kwargs):
        loop = asyncio.get_event_loop()
        redis = await storage.get_async_redis(loop)

        session = request.cookies.get('session')
        is_authorized = session and redis.exists(session)

        if is_authorized:
            response = await f(request, *args, **kwargs)
            return response
        else:
            return json({'status': 'not_authorized'}, 403)

    return wrapper


@app.websocket("/api/subscribe/")
async def subscribe_handler(_request, ws):
    data = await ws.recv()
    try:
        decoded_data = ujson.decode(data)
    except ValueError:
        await ws.send(ujson.dumps({'error': 'invalid json data'}))
        return

    token = decoded_data.get('token', '')

    loop = asyncio.get_event_loop()
    redis = await storage.get_async_redis(loop)

    mpsc = Receiver(loop=loop)
    await redis.subscribe(mpsc.channel(f'updates:{token}'))
    async for channel, msg in mpsc.iter():
        await ws.send(msg.decode())


@app.websocket("/api/code/")
async def code_handler(_request, ws):
    loop = asyncio.get_event_loop()
    redis = await storage.get_async_redis(loop)
    sender_id = secrets.token_hex(5)
    await ws.send(ujson.dumps({'sender_id': sender_id}))

    dmp = diff_match_patch()

    while True:
        data = await ws.recv()
        try:
            decoded_data = ujson.decode(data)
        except ValueError:
            await ws.send(ujson.dumps({'error': 'invalid json data'}))
            continue

        token = decoded_data['token']
        diff = decoded_data['diff']

        cur_data = await redis.get(token) or b''
        cur_data = cur_data.decode()

        try:
            patch = dmp.patch_fromText(diff)
        except ValueError:
            await ws.send(ujson.dumps({'error': 'invalid patch'}))
            continue

        new_data, _ = dmp.patch_apply(patch, cur_data)

        if len(new_data) > 32768:
            await ws.send(ujson.dumps({'error': 'code too long'}))
            continue

        await redis.set(token, new_data)

        publish_data = ujson.dumps({
            'sender_id': sender_id,
            'data': diff,
        })
        await redis.publish(f'updates:{token}', publish_data)


@app.route('/api/register/', methods=['POST', 'OPTIONS'])
async def register(request):
    if request.method == 'OPTIONS':
        return json({'status': 'ok'})

    if not request.json:
        return json({'error': 'only json'}, status=400)

    username = request.json.get('username')
    password = request.json.get('password')
    if not username or not password:
        return json({'error': 'fill all fields'}, status=400)
    if len(username) < 5:
        return json({'error': 'too short username'}, status=400)

    loop = asyncio.get_event_loop()
    redis = await storage.get_async_redis(loop)
    try:
        await storage.add_user(redis, username, password)
    except exceptions.UserExistsException:
        return json({'error': 'username taken'}, status=400)

    return json({'status': 'ok'})


@app.route('/api/login/', methods=['POST', 'OPTIONS'])
async def login(request):
    if request.method == 'OPTIONS':
        return json({'status': 'ok'})

    if not request.json:
        return json({'error': 'only json'}, status=400)

    username = request.json.get('username')
    password = request.json.get('password')
    if not username or not password:
        return json({'error': 'fill all fields'}, status=400)

    loop = asyncio.get_event_loop()
    redis = await storage.get_async_redis(loop)
    user = await storage.get_user(redis, username)
    if not user:
        return json({'error': 'invalid credentials'}, status=403)
    if user.get('password', '') != password:
        return json({'error': 'invalid credentials'}, status=403)

    session = secrets.token_hex(30)
    await storage.set_session(redis, session, user)

    response = json({'status': 'ok'})
    response.cookies['session'] = session
    response.cookies['session']['httponly'] = True
    return response


@app.route('/api/logout/')
async def logout(_request):
    response = json({'status': 'ok'})
    del response.cookies['session']
    return response


@app.route('/api/me/')
@login_required
async def me(request):
    loop = asyncio.get_event_loop()
    redis = await storage.get_async_redis(loop)

    user = await storage.get_current_user(redis, request)
    return json(user)


@app.route('/api/my_collabs/')
@login_required
async def list_my_collabs(request):
    loop = asyncio.get_event_loop()
    redis = await storage.get_async_redis(loop)

    user = await storage.get_current_user(redis, request)
    collabs = await storage.get_users_collabs(redis, user['username'])
    return json(collabs)


@app.route('/api/users/')
async def list_users(request):
    loop = asyncio.get_event_loop()
    redis = await storage.get_async_redis(loop)
    limit = request.args.get('limit', 10)
    offset = request.args.get('offset', 0)
    try:
        limit = int(limit)
        offset = int(offset)
    except Exception as e:
        return json({'error': str(e)}, status=400)

    limit = max(1, min(50, limit))

    users = await storage.get_users_listing(redis, limit, offset)
    return json(users)


@app.route('/api/new_collab/', methods=['POST', 'OPTIONS'])
@login_required
async def new_collab(request):
    if request.method == 'OPTIONS':
        return json({'status': 'ok'})

    if not request.json:
        return json({'error': 'only json'}, status=400)

    loop = asyncio.get_event_loop()
    redis = await storage.get_async_redis(loop)

    token = await storage.add_collab(redis, request)

    return json({'token': token})


# noinspection PyUnresolvedReferences
@app.route('/api/get_collab/<token>/')
async def get_collab(_request, token):
    loop = asyncio.get_event_loop()
    redis = await storage.get_async_redis(loop)

    data = await redis.get(token)
    f = await redis.get(f'code:{token}:format')
    return json({'data': data, 'format': f})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, protocol=WebSocketProtocol)