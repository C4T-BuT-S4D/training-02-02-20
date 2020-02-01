#!/usr/bin/env python3

from diff_match_patch import diff_match_patch

from collacode_lib import *

import gevent.monkey

gevent.monkey.patch_all()


class Checker(BaseChecker):
    def __init__(self, *args, **kwargs):
        super(Checker, self).__init__(*args, **kwargs)
        self.dmp = diff_match_patch()
        self.mch = CheckMachine(self.host)

    def action(self, action, *args, **kwargs):
        try:
            super(Checker, self).action(action, *args, **kwargs)
        except requests.exceptions.ConnectionError:
            cquit(Status.DOWN, 'Connection error')
        except websocket._exceptions.WebSocketConnectionClosedException:
            cquit(Status.DOWN, 'Websocket closed unexpectedly')

    def check(self, *_args, **_kwargs):
        username, password = self.mch.register()
        users = self.mch.get_user_listing()
        assert_in(username, users, 'Could not find user in listing')
        sess = self.mch.login(username, password)
        me = self.mch.get_me(sess)

        assert_in('username', me, 'Invalid me')
        assert_in('password', me, 'Invalid me')
        assert_eq(me['username'], username, 'Invalid me')
        assert_eq(me['password'], password, 'Invalid me')

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
            assert_eq(result, diff, 'Invalid data returned from collab socket')

            cur_data += block

        full = self.mch.get_collab(sess, collab_token)
        assert_eq(full['format'], f, 'Invalid collab format')
        assert_eq(full['data'], data, 'Invalid collab data')

        collabs = self.mch.get_my_collabs(sess)
        assert_in(collab_token, collabs, 'Collab not found in listing')

        cquit(Status.OK)

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

        assert_eq(result, diff, 'Invalid data returned from collab socket')

        cquit(Status.OK, f"{username}:{password}:{collab_token}")

    def get(self, flag, flag_id, *_args, **_kwargs):
        default_status = status.Status.CORRUPT

        username, password, collab_token = flag_id.split(':')
        sess = self.mch.login(username, password)

        my_collabs = self.mch.get_my_collabs(sess)
        assert_in(
            collab_token, my_collabs,
            'Could not find collab in my listing',
            status=default_status,
        )

        s = get_initialized_session()
        collab = self.mch.get_collab(s, collab_token)
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
