


import mysql.connector

def insertBLOB(image, photo):
    print("Inserting BLOB into table")
    try:
        connection = mysql.connector.connect(host='localhost',
                                             database='',
                                             user='dbuser',
                                             password='dbpass')

        cursor = connection.cursor()

        sql = """INSERT INTO asset.inventory
                          (sn, name, description, value, picture, json, note) VALUES (%s,%s,%s,%s,%s,%s,%s)"""

        with open(photo, 'rb') as f:
            blob = f.read()


        # Convert data into tuple format
        data = (image, image, None, None, blob, None, None)

        result = cursor.execute(sql, data)
        connection.commit()
        print("Image file inserted successfully as a BLOB into table", result)

    except mysql.connector.Error as error:
        print("Failed inserting BLOB data into MySQL table {}".format(error))

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")


insertBLOB('001_image.png', 'image.png')


