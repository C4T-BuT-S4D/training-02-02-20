from checklib import *
from bs4 import BeautifulSoup

PORT = 4000


class CheckMachine:
    @property
    def url(self):
        return f'http://{self.host}:{self.port}'

    def __init__(self, host):
        self.host = host
        self.port = PORT

    def register_user(self, username=None, password=None):
        username = username or rnd_username()
        password = password or rnd_password()

        sess = get_initialized_session()

        r = sess.post(f'{self.url}/register', data={'login': username, 'password': password})
        check_response(r, 'Could not register')
        return username, password, sess

    def login_user(self, username, password):
        sess = get_initialized_session()
        r = sess.post(f'{self.url}/login', data={'login': username, 'password': password})
        check_response(r, 'Could not login')
        return sess

    def upload_video(self, sess, description, caption, webm_path, private=True):
        data = {'description': description, 'subtitles': caption, "private": "on" if private else "off"}
        with open(webm_path, 'rb') as webm_file:
            files = {'video': webm_file}
            r = sess.post(f'{self.url}/create', data=data, files=files)
            check_response(r, 'Could not create video')
            v_id = r.url[r.url.rfind('/') + 1:]
            return v_id, r.url

    def get_my_video_info(self, sess):
        r = sess.get(f'{self.url}/home')
        check_response(r, 'Could not get home page')
        sp = BeautifulSoup(r.text, features="lxml")
        video_info = {}
        for v_div in sp.find_all("div", {"class": "ui secondary segment"}):
            p_s = v_div.find_all('p')
            v_id = p_s[0].text.split()[-1]
            video_info[v_id] = {}
            descr = p_s[2].text
            video_info[v_id]['description'] = descr.split()[-1]
            video_info[v_id]['token'] = ''
            video_info[v_id]['watch_link'] = v_div.a.get('href')
            video_info[v_id]['preview_path'] = v_div.img.get('src')

            if len(p_s) > 3:
                video_info[v_id]['token'] = p_s[-1].text.split()[-1]

        return video_info

    def get_watch_info(self, w_url, sess=None):
        if sess is None:
            sess = get_initialized_session()
        r = sess.get(w_url)
        check_response(r, 'Could not watch video')
        sp = BeautifulSoup(r.text, features='lxml')

        watch_info = {'video': sp.video.source.get('src'), 'track': sp.video.track.get('src'),
                      'desc': sp.find('h4', attrs={'class': 'ui header'}).text}
        return watch_info

    def check_preview(self, preview_path, sess=None):
        r = sess.get(f'{self.url}/{preview_path}', headers={'Range': 'bytes=0-99'})
        check_response(r, 'Failed to get video preview')
        if int(r.headers['Content-Length']) < 100 or 'PNG' not in r.text:
            cquit(status.Status.MUMBLE, 'Failed to get video preview', f'Error on {r.url}: {r.status_code}')

    def get_track_content(self, track_path, sess=None):
        if sess is None:
            sess = get_initialized_session()
        r = sess.get(f'{self.url}{track_path}')
        check_response(r, 'Failed to get subtitles content')
        return r.text

    def check_video(self, video_path, sess=None):
        if sess is None:
            sess = get_initialized_session()
        r = sess.get(f'{self.url}{video_path}', headers={'Range': 'bytes=0-99'})
        check_response(r, 'Failed to get video content')
        if int(r.headers['Content-Length']) < 100 or 'webm' not in r.text:
            cquit(status.Status.MUMBLE, 'Failed to get video content', f'Error on {r.url}: {r.status_code}')
        return r.text

    def get_access(self, sess, v_id, token):
        r = sess.post(f'{self.url}/access', data={'videoID': v_id, 'token': token})
        check_response(r, "Failed to get access using private key")
        return r.url


# print(sp.find_all("div", {"class": "ui secondary segment"}))


if __name__ == '__main__':
    get_text_webm(
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi" + "=",
        "test")
