#!/usr/bin/env python3

import sys

from diff_match_patch import diff_match_patch

from collacode_lib import *


def put(host, flag_id, flag, _vuln):
    dmp = diff_match_patch()

    mch = CheckMachine(host)
    username, password = mch.register()
    sess = mch.login(username, password)

    f = 'json'
    data = json.dumps(
        {
            'flag': flag,
            'flag_id': flag_id,
        },
    )
    patch = dmp.patch_make('', data)
    diff = dmp.patch_toText(patch)

    collab_token = mch.new_collab(sess, f)

    collab_in_ws = mch.get_collab_in_ws(collab_token)
    collab_out_ws = mch.get_collab_out_ws()

    mch.send_collab_data(collab_out_ws, collab_token, diff)
    result = mch.recv_collab_data(collab_in_ws)

    assert_eq(result, diff.encode(), 'Invalid data returned from collab socket')

    cquit(Status.OK, f"{username}:{password}:{collab_token}")


def get(host, flag_id, flag, _vuln):
    default_status = status.Status.CORRUPT
    mch = CheckMachine(host)
    username, password, collab_token = flag_id.split(':')
    sess = mch.login(username, password)

    my_collabs = mch.get_my_collabs(sess)
    assert_in(
        collab_token, my_collabs,
        'Could not find collab in my listing',
        status=default_status,
    )

    s = get_initialized_session()
    collab = mch.get_collab(s, collab_token)
    assert_eq(collab['format'], 'json', 'Invalid collab format', status=default_status)
    with handle_exception(
            ValueError,
            public='Invalid collab data',
            private='JSON decode exception while checking collab',
            status=default_status):
        collab_data = json.loads(collab['data'])

    assert_in('flag', collab_data, 'No flag in collab', status=default_status)
    assert_eq(flag, collab_data['flag'], 'Invalid flag in collab', status=default_status)

    cquit(Status.OK)


def check(host):
    dmp = diff_match_patch()

    mch = CheckMachine(host)
    username, password = mch.register()
    users = mch.get_user_listing()
    assert_in(username, users, 'Could not find user in listing')
    sess = mch.login(username, password)
    me = mch.get_me(sess)

    assert_in('username', me, 'Invalid me')
    assert_in('password', me, 'Invalid me')
    assert_eq(me['username'], username, 'Invalid me')
    assert_eq(me['password'], password, 'Invalid me')

    f, data = mch.random_data()
    collab_token = mch.new_collab(sess, f)

    collab_in_ws = mch.get_collab_in_ws(collab_token)
    collab_out_ws = mch.get_collab_out_ws()

    blocks = [data[i:i + 100] for i in range(0, len(data), 100)]

    cur_data = ''
    for block in blocks:
        patch = dmp.patch_make(cur_data, cur_data + block)
        diff = dmp.patch_toText(patch)

        mch.send_collab_data(collab_out_ws, collab_token, diff)
        result = mch.recv_collab_data(collab_in_ws)
        assert_eq(result, diff.encode(), 'Invalid data returned from collab socket')

        cur_data += block

    full = mch.get_collab(sess, collab_token)
    assert_eq(full['format'], f, 'Invalid collab format')
    assert_eq(full['data'], data, 'Invalid collab data')

    collabs = mch.get_my_collabs(sess)
    assert_in(collab_token, collabs, 'Collab not found in listing')

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
    except websocket._exceptions.WebSocketConnectionClosedException:
        cquit(Status.DOWN, 'Websocket closed unexpectedly')
    except SystemError as e:
        raise
    except Exception as e:
        print(f'Got checksystem exception {e} {type(e)} {repr(e)}')
        cquit(Status.ERROR, 'System error', str(e))
