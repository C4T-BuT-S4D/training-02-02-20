#!/usr/bin/env python3
import sys

import requests

from checklib import *

from kek_lib import *


def check(host):
    cm = CheckMachine(host)

    username = rnd_username()
    password = rnd_password()

    cm.register_user(username, password)
    token = cm.login_user(username, password)
    cm.select_token(token)

    section_id = cm.create_section(True)

    sections = cm.enumerate_last_sections()

    found = None
    for section in sections:
        if section["id"] == section_id:
            found = section

    if found is None:
        cquit(Status.MUMBLE, 'Did not find a freshly created section')

    assert_in('owner', found, 'Section enumeration does not have owners listed')

    post_id, title = cm.create_post(section_id, rnd_string(40))

    posts = cm.get_section_posts(section_id)
    assert_gt(len(posts), 0, 'Could not find created post')
    assert_eq(posts[0]["id"], post_id, 'Could not find created post')

    user2 = rnd_username()
    pass2 = rnd_password()
    user2_id = cm.register_user(user2, pass2)
    token2 = cm.login_user(username, password)
    cm.invite_to_section(section_id, user2_id)

    cm.select_token(token2)
    cm.get_section_posts(section_id)
    assert_gt(len(posts), 0, 'Could not find created post as invited user')
    assert_eq(posts[0]["id"], post_id, 'Could not find created post as invited user')

    ans = [x["id"] for x in cm.search_posts(title.split()[0])]

    if post_id not in ans:
        cquit(Status.MUMBLE, "Could not search a post in private section")

    cquit(Status.OK)


def put(host, flag_id, flag, vuln):
    cm = CheckMachine(host)

    username = rnd_username()
    password = rnd_password()

    cm.register_user(username, password)
    token = cm.login_user(username, password)
    cm.select_token(token)

    section_id = cm.create_section(True)

    _, _ = cm.create_post(section_id, flag)

    answer = f'{username}:{password}:{section_id}'
    cquit(Status.OK, answer)


def get(host, flag_id, flag, vuln):
    cm = CheckMachine(host)

    username, password, section_id = flag_id.split(":")
    token = cm.login_user(username, password)
    cm.select_token(token)

    posts = cm.get_section_posts(section_id)

    found = False
    for post in posts:
        if post.get("description") == flag:
            found = True

    if not found:
        cquit(Status.CORRUPT, "Flag not found")

    cquit(Status.OK)


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
    except requests.exceptions.ConnectionError:
        cquit(Status.DOWN, 'Connection error')
    except SystemError as e:
        raise
    except Exception as e:
        print(f'Got checksystem exception {e} {type(e)} {repr(e)}')
        cquit(Status.ERROR, 'System error', str(e))
