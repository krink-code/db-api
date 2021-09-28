#!/usr/bin/env python3

import requests

username='dbapi'
password='dbapi'

response = requests.post('http://localhost:8980/api/example/table1',
               auth=requests.auth.HTTPBasicAuth(username, password),
               json={"name":"lalala","description":"not much"})

print(response.json())
print(response.ok)
