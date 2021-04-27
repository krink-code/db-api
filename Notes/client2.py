#!/usr/bin/env python3

import requests
res = requests.post('http://localhost:8980/api/example/table1', json={"name":"lalala"})
if res.ok:
    print(res.json())
else:
    print(res)

