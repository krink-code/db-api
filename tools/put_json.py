#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__version__='put_json_0.0.1'

import sys
import json
import requests
import select

# ./put_json.py --user dbuser:dbpass test2.jpg test2.json http://127.0.0.1:8980/api/example2/table2
# cat test2.json | ./put_json.py --user dbuser:dbpass test2.jpg - http://127.0.0.1:8980/api/example2/table2

def Usage():
    print('Usage: ' + sys.argv[0] + """ --user dbuser:dbpass name file.json url

        --user    is the database user and password
        name      is the name or id of the image
        file.json is the file containing json
        url       is the destination url            

    """)

try:
    userpass  = sys.argv[2]
    name      = sys.argv[3]
    json_file = sys.argv[4]
    url       = sys.argv[5]
except IndexError:
    Usage()
    sys.exit(1)

username = userpass.split(":")[0]
password = userpass.split(":")[1]

if select.select([sys.stdin,],[],[],0.0)[0]:
    json_data = json.load(sys.stdin)
else:
    with open(json_file, 'r') as jfile:
        json_data = json.load(jfile)


response = requests.put(url,
               auth=requests.auth.HTTPBasicAuth(username, password),
               json={"image": name, "json": json.dumps(json_data) })

print(response.text)

