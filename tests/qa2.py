#!/usr/bin/env python3

import sys
import requests

username = 'dbuser'
password = 'dbpass'
origin = 'http://127.0.0.1:8980'

# insert via post json

url = origin + '/api/example/table1'

post = requests.post(url,
               auth=requests.auth.HTTPBasicAuth(username, password),
               json={"name":"qa1","description":"posted via qa1"})

print(post.text)
print(post.ok)
print(post.status_code)


