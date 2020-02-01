import random

from checklib import *

PORT = 4455


class CheckMachine:
    @property
    def url(self):
        return f'http://{self.host}:{self.port}'

    def __init__(self, host):
        self.host = host
        self.port = PORT
        self.token = None

    def register_user(self, username=None, password=None):
        username = username or rnd_username()
        password = password or rnd_password()

        sess = get_initialized_session()

        r = sess.post(f'{self.url}/api/auth/register', data={'username': username, 'password': password})
        check_response(r, 'Could not register')
        data = get_json(r, 'Could not register')
        assert_in('user', data, 'Could not register')
        assert_in('id', data['user'], 'Could not register')

        return data["user"]["id"]

    def login_user(self, username, password):
        sess = get_initialized_session()
        r = sess.post(f'{self.url}/api/auth/login', data={'username': username, 'password': password})

        check_response(r, 'Could not login')
        data = get_json(r, 'Could not login')
        assert_in('token', data, 'Could not login')
        assert_in('token', data['token'], 'Could not login')

        return data["token"]["token"]

    def select_token(self, token):
        self.token = token

    def create_section(self, private=False):
        sess = get_initialized_session()

        section_title = rnd_string(20)
        r = sess.post(f'{self.url}/api/sections',
                      data={'title': section_title, 'description': rnd_string(50), "is_private": int(private), "token": self.token})

        check_response(r, 'Could not create section')
        data = get_json(r, 'Could not create section')
        assert_in('section', data, 'Could not create section')
        assert_in('id', data['section'], 'Could not create section')

        section_id = data["section"]["id"]
        return section_id

    def create_post(self, section_id, content=None):
        sess = get_initialized_session()

        if content is None:
            content = rnd_string(40)

        title = rnd_string(24)

        r = sess.post(f'{self.url}/api/posts',
                      data={'title': title, 'description': content, 'type': 'image', 'src': random.choice([
                          "https://avatars.mds.yandex.net/get-pdb/2346993/4c247688-b382-4df6-9770-22ff9c058014/s1200"
                      ]), "section_id": section_id, "token": self.token})

        check_response(r, 'Could not create post')
        data = get_json(r, 'Could not create post')
        assert_in('post', data, 'Could not create post')
        assert_in('id', data['post'], 'Could not create post')


        post_id = data["post"]["id"]

        return post_id, title

    def get_section_posts(self, section_id):
        sess = get_initialized_session()

        r = sess.get(f'{self.url}/api/sections/{section_id}/posts')
        check_response(r, 'Could not load section posts')
        data = get_json(r, 'Could not load section posts')
        assert_in('posts', data, 'Could not load section posts')

        return data["posts"]

    def invite_to_section(self, section_id, user2_id):
        sess = get_initialized_session()

        r = sess.post(f'{self.url}/api/sections/{section_id}/invite', {
            "whom": user2_id,
            "token": self.token
        })
        
        check_response(r, "Could not invite user")
        data = get_json(r, "Could not invite user")

        assert_in('status', data, "Could not invite user")
        assert_eq(data["status"], "ok", "Could not invite user")

    def enumerate_last_sections(self):
        sess = get_initialized_session()

        r = sess.get(f'{self.url}/api/sections')

        check_response(r, "Could not load sections")
        data = get_json(r, "Could not load sections")
        assert_in('sections', data, "Could not load sections")

        return data["sections"]

    def search_posts(self, word):
        sess = get_initialized_session()

        r = sess.get(f'{self.url}/api/search/private?token=' + self.token + "&q=" + word)

        check_response(r, "Could not search")
        data = get_json(r, "Could not search")
        assert_in('posts', data, "Could not search")

        return data["posts"]
