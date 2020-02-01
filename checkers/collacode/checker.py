#!/usr/bin/env python3

import os
import sys
import gevent.monkey


sys.path.append(os.path.dirname(os.path.abspath(__file__)))
gevent.monkey.patch_all()


from diff_match_patch import diff_match_patch

from collacode_lib import *


class Checker(BaseChecker):
    def __init__(self, *args, **kwargs):
        super(Checker, self).__init__(*args, **kwargs)
        self.dmp = diff_match_patch()
        self.mch = CheckMachine(self)

    def action(self, action, *args, **kwargs):
        try:
            super(Checker, self).action(action, *args, **kwargs)
        except requests.exceptions.ConnectionError:
            self.cquit(Status.DOWN, 'Connection error')
        except websocket._exceptions.WebSocketConnectionClosedException:
            self.cquit(Status.DOWN, 'Websocket closed unexpectedly')

    def check(self, *_args, **_kwargs):
        username, password = self.mch.register()
        users = self.mch.get_user_listing()
        self.assert_in(username, users, 'Could not find user in listing')
        sess = self.mch.login(username, password)
        me = self.mch.get_me(sess)

        self.assert_in('username', me, 'Invalid me')
        self.assert_in('password', me, 'Invalid me')
        self.assert_eq(me['username'], username, 'Invalid me')
        self.assert_eq(me['password'], password, 'Invalid me')

        f, data = self.mch.random_data()
        collab_token = self.mch.new_collab(sess, f)

        collab_in_ws = self.mch.get_collab_in_ws(collab_token)
        collab_out_ws = self.mch.get_collab_out_ws()

        blocks = [data[i:i + 100] for i in range(0, len(data), 100)]

        cur_data = ''
        for block in blocks:
            patch = self.dmp.patch_make(cur_data, cur_data + block)
            diff = self.dmp.patch_toText(patch)

            self.mch.send_collab_data(collab_out_ws, collab_token, diff)
            result = self.mch.recv_collab_data(collab_in_ws)
            self.assert_eq(result, diff, 'Invalid data returned from collab socket')

            cur_data += block

        full = self.mch.get_collab(sess, collab_token)
        self.assert_eq(full['format'], f, 'Invalid collab format')
        self.assert_eq(full['data'], data, 'Invalid collab data')

        collabs = self.mch.get_my_collabs(sess)
        self.assert_in(collab_token, collabs, 'Collab not found in listing')

        self.cquit(Status.OK)

    def put(self, flag, flag_id, *_args, **_kwargs):
        username, password = self.mch.register()
        sess = self.mch.login(username, password)

        f = 'json'
        data = json.dumps(
            {
                'flag': flag,
                'flag_id': flag_id,
            },
        )
        patch = self.dmp.patch_make('', data)
        diff = self.dmp.patch_toText(patch)

        collab_token = self.mch.new_collab(sess, f)

        collab_in_ws = self.mch.get_collab_in_ws(collab_token)
        collab_out_ws = self.mch.get_collab_out_ws()

        self.mch.send_collab_data(collab_out_ws, collab_token, diff)
        result = self.mch.recv_collab_data(collab_in_ws)

        self.assert_eq(result, diff, 'Invalid data returned from collab socket')

        self.cquit(Status.OK, f"{username}:{password}:{collab_token}")

    def get(self, flag, flag_id, *_args, **_kwargs):
        default_status = status.Status.CORRUPT

        username, password, collab_token = flag_id.split(':')
        sess = self.mch.login(username, password)

        my_collabs = self.mch.get_my_collabs(sess)
        self.assert_in(
            collab_token, my_collabs,
            'Could not find collab in my listing',
            status=default_status,
        )

        s = get_initialized_session()
        collab = self.mch.get_collab(s, collab_token)
        self.assert_eq(collab['format'], 'json', 'Invalid collab format', status=default_status)
        try:
            collab_data = json.loads(collab['data'])
        except ValueError:
            self.cquit(default_status, 'Invalid collab data', 'JSON decode exception while checking collab')
            

        self.assert_in('flag', collab_data, 'No flag in collab', status=default_status)
        self.assert_eq(flag, collab_data['flag'], 'Invalid flag in collab', status=default_status)

        self.cquit(Status.OK)
