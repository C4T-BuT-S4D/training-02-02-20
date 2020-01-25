#!/usr/bin/env python3
import hashlib
import sys
import tempfile
import random

import requests

import imagegen
from tiktak_lib import *
from checklib import *
import os

rand_words = [
    'ya', 'sosal', 'shit', 'some', 'text', 'wow', 'ctf', 'flag', 'l33t', 'ctf', 'eto', 'minin', 'hudorozka', 'cbs',
    'menya', 'ebali', 'pr', 'python', 'smm', 'byl', 'by', 'ty', 'chelovekom', 'batya', 'kek', 'lol', 'arbidol'
]


def get_webms():
    return ['webms/' + x for x in os.listdir('webms') if not x.startswith('.')]


def get_random_webm():
    return random.choice(get_webms())


def get_random_caption():
    return '\n'.join([random.choice(rand_words) for _ in range(3)])


def get_random_description():
    ans = []
    for i in range(3):
        j = random.randint(0, len(rand_words) - 2)
        ans.append(rand_words[j])
        ans.append(rand_words[j + 1])
    return ' '.join(ans)


def get_hash(b):
    return hashlib.sha1(b).hexdigest()


def get_file_hash(path, n=1000):
    f = open(path, 'rb')
    hsh = get_hash(f.read(n))
    f.close()
    return hsh


def check(host):
    cm = CheckMachine(host)
    u, p, _ = cm.register_user()
    sess = cm.login_user(u, p)
    description = get_random_description()
    caption = get_random_caption()
    webm = get_random_webm()
    if webm.endswith("gocr.webm"):
        description = "Who the fuck is your gocr"
        caption = '\n'.join(["Да кто такой", "этот ваш", "gocr нахуй"])
    webm_hash = get_file_hash(webm)
    v_id, w_link = cm.upload_video(sess, description, caption, webm, private=False)
    info = cm.get_my_video_info(sess)
    cm.check_preview(info[v_id]['preview_path'], sess)

    # Do a query as unauthorized user
    sess = get_initialized_session()
    w_info = cm.get_watch_info(w_link, sess)

    if description not in w_info['desc']:
        cquit(status.Status.MUMBLE, "Failed to get video description")
    track_content = cm.get_track_content(w_info['track'], sess)
    if caption.split()[0] not in track_content:
        cquit(status.Status.MUMBLE, "Failed to get subtitles content")

    video_content = cm.check_video(w_info['video'])
    if get_hash(video_content) != webm_hash:
        cquit(status.Status.MUMBLE, "Failed to get video content")


def put(host, _flag_id, flag, _vuln):
    cm = CheckMachine(host)
    u, p, sess = cm.register_user()

    caption = get_random_caption()
    description = get_random_description()
    video_content = rnd_string(30)
    if _vuln == 0:
        caption = flag
    elif _vuln == 1:
        description = flag
    else:
        video_content = flag

    with tempfile.TemporaryDirectory() as tmp_dir_name:
        o_path = tmp_dir_name + '/video'
        webm_path = imagegen.get_text_webm(video_content, o_path)
        webm_hash = get_file_hash(webm_path)
        v_id, w_link = cm.upload_video(sess, description, caption, webm_path, private=True)

    v_info = cm.get_my_video_info(sess)

    cm.check_preview(v_info[v_id]['preview_path'], sess)
    token = v_info[v_id].get('token')
    if token is None:
        cquit(Status.MUMBLE, "Can't get token for private video", v_info)

    flag_id_s = f'{description}:{caption.split()[0]}:{webm_hash}:{v_id}:{token}'
    cquit(Status.OK, flag_id_s)


def get(host, flag_id, flag, _vuln):
    description, caption, webm_hash, v_id, token = flag_id.strip().split(":")
    cm = CheckMachine(host)

    _, _, sess = cm.register_user()

    w_link = cm.get_access(sess, v_id, token)

    w_info = cm.get_watch_info(w_link, sess)

    if description not in w_info['desc']:
        cquit(status.Status.CORRUPT, "Failed to get video description")

    track_content = cm.get_track_content(w_info['track'], sess)

    if caption not in track_content:
        cquit(status.Status.CORRUPT, "Failed to get subtitles content")

    video_content = cm.check_video(w_info['video'], sess)
    if get_hash(video_content) != webm_hash:
        cquit(status.Status.CORRUPT, "Failed to get video content")


if __name__ == '__main__':
    action, *args = sys.argv[1:]
try:

    if action == "check":
        host, = args
        check(host)
    elif action == "put":
        host, flag_id, flag, vuln = args
        put(host, flag_id, flag, vuln)
    elif action == "get":
        host, flag_id, flag, vuln = args
        get(host, flag_id, flag, vuln)
    else:
        cquit(Status.ERROR, 'System error', 'Unknown action: ' + action)

    cquit(Status.ERROR)
except (requests.exceptions.ConnectionError, requests.exceptions.ConnectTimeout):
    cquit(Status.DOWN, 'Connection error')
except SystemError as e:
    raise
except Exception as e:
    cquit(Status.ERROR, 'System error', str(e))
