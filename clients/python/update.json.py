
# -*- coding: utf-8 -*-

import mysql.connector
import json

data = {'json': True, 'string': 'testing', 'integer': 1, 'url': None}

db = mysql.connector.connect(user="dbuser",password="dbpass",host="localhost")

cursor = db.cursor()
sql = "update asset.inventory set json = %s where sn='sn001'"
cursor.execute(sql,(json.dumps(data),))
db.commit()
db.close()


