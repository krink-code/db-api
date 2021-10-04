
# -*- coding: utf-8 -*-

import mysql.connector

picture = 'image.png'

with open(picture, 'rb') as f:
    photo = f.read()


#import base64
#encodestring = base64.b64encode(photo)

db = mysql.connector.connect(user="dbuser",password="dbpass",host="localhost",database="")

cursor = db.cursor()
#sql = "insert into sample values(%s)"
sql = "update asset.inventory set picture = %s where sn='sn001'"
#cursor.execute(sql,(encodestring,))
cursor.execute(sql,(photo,))
db.commit()
db.close()


