import json
import random

import requests
import websocket
from checklib import *

PORT = 9997


class CheckMachine:
    @property
    def url(self):
        return f'http://{self.host}:{self.port}/api'

    def __init__(self, host):
        self.host = host
        self.port = PORT

    def register(self):
        url = f'{self.url}/register/'
        username = rnd_username()
        password = rnd_password()
        data = {
            'username': username,
            'password': password
        }
        r = requests.post(url, json=data)

        check_response(r, 'Could not register')
        data = get_json(r, 'Invalid response from register')
        assert_eq(data, {'status': 'ok'}, 'Could not register')

        return username, password

    def login(self, username, password):
        sess = get_initialized_session()
        url = f'{self.url}/login/'

        data = {
            'username': username,
            'password': password
        }
        r = sess.post(url, json=data)

        check_response(r, 'Could not login')
        data = get_json(r, 'Invalid response from login')
        assert_eq(data, {'status': 'ok'}, 'Could not login')

        return sess

    def get_me(self, sess):
        url = f'{self.url}/me/'

        r = sess.get(url)

        check_response(r, 'Could not get me page')
        data = get_json(r, 'Invalid response from me')

        return data

    def get_user_listing(self):
        url = f'{self.url}/users/?limit=50&offset=0'

        r = requests.get(url)

        check_response(r, 'Could not get user listing')
        data = get_json(r, 'Invalid response from user listing')
        assert_eq(type(data), dict, 'Invalid response from user listing')
        assert_in('count', data, 'Invalid response from user listing')
        assert_in('users', data, 'Invalid response from user listing')

        return data['users']

    def new_collab(self, sess, f):
        url = f'{self.url}/new_collab/'

        r = sess.post(url, json={'format': f})
        check_response(r, 'Could not create new collab')
        data = get_json(r, 'Invalid response from new collab')
        assert_in('token', data, 'Invalid response from new collab')

        return data['token']

    def get_collab(self, sess, token):
        url = f'{self.url}/get_collab/{token}/'

        r = sess.get(url)
        check_response(r, 'Could not get collab')
        data = get_json(r, 'Invalid response from get collab')
        assert_in('data', data, 'Invalid response from get collab')
        assert_in('format', data, 'Invalid response from get collab')

        return data

    def get_my_collabs(self, sess):
        url = f'{self.url}/my_collabs/'

        r = sess.get(url)
        check_response(r, 'Could not get my collabs')
        data = get_json(r, 'Invalid response from get my collabs')
        assert_eq(type(data), list, 'Invalid response from get my collabs')

        return data

    def get_collab_in_ws(self, token):
        ws = websocket.WebSocket()
        url = f'ws://{self.host}:{self.port}/api/subscribe/'
        ws.connect(url)
        ws.send(json.dumps({"token": token}))
        assert_eq(101, ws.status, 'Invalid ws status on subscribe')
        return ws

    def get_collab_out_ws(self):
        ws = websocket.WebSocket()
        url = f'ws://{self.host}:{self.port}/api/code/'
        ws.connect(url)
        data = ws.recv()
        try:
            decoded = json.loads(data)
        except ValueError:
            cquit(Status.MUMBLE, 'Invalid data from code websocket')
        assert_in('sender_id', data, 'sender_id not returned for code websocket')

        return ws

    @staticmethod
    def send_collab_data(ws, token, data):
        to_send = json.dumps({
            'token': token,
            'diff': data,
        })
        return ws.send(to_send)

    @staticmethod
    def recv_collab_data(ws):
        encoded = ws.recv()
        try:
            resp = json.loads(encoded)
        except (ValueError, UnicodeDecodeError):
            cquit(Status.MUMBLE, 'Invalid data from code websocket')
        else:
            assert_in('data', resp, 'Invalid data from code websocket')
            assert_in('sender_id', resp, 'sender_id not returned for subscribe websocket')
            return resp['data']

    @staticmethod
    def json_generator():
        data = {
            rnd_string(random.randint(10, 20)): rnd_string(random.randint(10, 20))
            for _ in range(random.randint(10, 20))
        }
        return json.dumps(data)

    @staticmethod
    def c_generator():
        template = '''
        #include <stdio.h>
        
        int main() {{
            {data}
        }}
        '''

        data = '\n'.join(f'\t\tprintf("{rnd_string(10)}");')
        return template.format(data=data)

    @staticmethod
    def python_generator():
        blocks = [
            '''
for i in range(10):
    print(i)
''',
            '''
print(__import__("os").popen("ls").read())
''',
            '''
for j in range(150):
    print("PWNed!", end=' ')
''',
            '''
print('Love writing checkers')
''',
        ]

        cnt = random.randint(10, 20)
        return ''.join(random.choices(blocks, k=cnt))

    def get_generators(self):
        return [
            ('json', self.json_generator),
            ('c', self.c_generator),
            ('python', self.python_generator),
        ]

    def random_data(self):
        f, gen = random.choice(self.get_generators())
        return f, gen()
