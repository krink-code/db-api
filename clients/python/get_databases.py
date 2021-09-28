#!/usr/bin/env python3

import requests

username='dbapi'
password='dbapi'

response = requests.get('http://127.0.0.1:8980/api',
               auth=requests.auth.HTTPBasicAuth(username, password))

print(response.text)
print(response.json())
print(response.ok)

