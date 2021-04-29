
# python3

__version__='0.0.1.dev.20210428-4.mysql.connector.1'

from app import app
from flask import request
from flask import jsonify
from werkzeug.exceptions import HTTPException
#from werkzeug.exceptions import Unauthorized
#from db import mysql
#import cryptography
from functools import wraps

import mysql.connector
#https://github.com/mysql/mysql-connector-python
#https://dev.mysql.com/doc/connector-python/en/connector-python-example-connecting.html
#pip3 install mysql-connector-python

#config = {
#    'user': request.authorization.username,
#    'password': request.authorization.password,
#    'database': '',
#    'host': request.headers.get('X-Host', '127.0.0.1'),
#    'port': int(request.headers.get('X-Port', '3306')),
#    'raise_on_warnings': True,
#    'auth_plugin': 'mysql_native_password',
#}

#db = None
def sqlConnection():
    #global db
    config = {
        'user': request.authorization.username,
        'password': request.authorization.password,
        'database': '',
        'host': request.headers.get('X-Host', '127.0.0.1'),
        'port': int(request.headers.get('X-Port', '3306')),
        'raise_on_warnings': True,
        'auth_plugin': 'mysql_native_password',
    }
    db = mysql.connector.connect(**config)
    return db





#GET    /                             # Show status
@app.route("/", methods=['GET'])
def root():
    return jsonify(status=200, message="OK", version=__version__), 200


#GET    /api                          # Show databases
@app.route("/api", methods=['GET'])
def show_databases():
    SQL = 'SHOW DATABASES'
    rows = fetchall(SQL)

    return jsonify(rows), 200


#GET    /api/<db>                     # Show database tables
@app.route("/api/<db>", methods=['GET'])
def show_tables(db=None):
    assert db == request.view_args['db']
    SQL = 'SHOW TABLES FROM ' + str(db)
    rows = fetchall(SQL)
    return jsonify(rows), 200


#GET    /api/<db>/<table>             # Show database table fields
#GET    /api/<db>/<table>?query=true  # List rows of table
@app.route("/api/<db>/<table>", methods=['GET'])
def get_many(db=None, table=None):

    assert db == request.view_args['db']
    assert table == request.view_args['table']

    fields = request.args.get("fields", '*')
    limit  = request.args.get("limit", None)

    if not request.query_string:
        SQL = 'SHOW FIELDS FROM ' + str(db) +'.'+ str(table)
    else:
        SQL = 'SELECT '+ str(fields) +' FROM '+ str(db) +'.'+ str(table) 

    if limit:
        SQL += ' LIMIT ' + str(limit)

    rows = fetchall(SQL)

    if rows is None:
        return jsonify(status=404, message="Not Found"), 404
    else:
        return jsonify(rows), 200


#GET    /api/<db>/<table>/:id         # Retrieve a row by primary key
@app.route("/api/<db>/<table>/<key>", methods=['GET'])
def get_one(db=None, table=None, key=None):

    assert db == request.view_args['db']
    assert table == request.view_args['table']
    assert key == request.view_args['key']

    fields = request.args.get("fields", '*')

    SQL = "SELECT "+ str(fields) +" FROM "+ str(db) +"."+ str(table) +" WHERE id='"+str(key)+"'"

    row = fetchone(SQL)

    if row is None:
        return jsonify(status=404, message="Not Found"), 404
    else:
        return jsonify(row), 200


##POST   /api/<db>/<table>             # Create a new row
#@app.route("/api/<db>/<table>", methods=['POST'])
#def post_insert(db=None, table=None):
#
#    assert db == request.view_args['db']
#    assert table == request.view_args['table']
#
#    if not request.headers['Content-Type'] == 'application/json':
#        return jsonify(status=412, errorType="Precondition Failed"), 412
#
#    post = request.get_json()
#
#    placeholders = ['%s'] * len(post)
#    fields = ",".join([str(key) for key in post])
#    places = ",".join([str(key) for key in placeholders])
#
#    values=[]
#    for key in post:
#        values.append(post[key])
#
#    SQL = "INSERT INTO "+str(db)+"."+str(table)+" ("+str(fields)+") VALUES ("+str(places)+")"
#    print(SQL)
#
#    insert = insertsql(SQL, values)
#    return jsonify(status=201, message="Created"), 201
#
#    #if insert is True:
#    #    return jsonify(status=201, message="Created"), 201
#    #else:
#    #    return jsonify(status=461, message="Failed Create"), 461


# this works...

#POST   /api/<db>/<table>             # Create a new row
@app.route("/api/<db>/<table>", methods=['POST'])
def post_insert(db=None, table=None):

    assert db == request.view_args['db']
    assert table == request.view_args['table']


    if not request.headers['Content-Type'] == 'application/json':
        return jsonify(status=412, errorType="Precondition Failed"), 412

    post = request.get_json()

    #print(str(type(post)))
    #print(len(post))

    placeholders = ['%s'] * len(post)

    fields = ",".join([str(key) for key in post])
    places = ",".join([str(key) for key in placeholders])

    #print(fields)
    #print(places)

    #records = ['Jane', 'Another description']
    records=[]
    for key in post:
        records.append(post[key])

    SQL = "INSERT INTO " +str(db)+"."+str(table)+" ("+str(fields)+") VALUES ("+str(places)+")"

    #print(SQL)
    #insert = insertsql(SQL, records)
    #if insert == True:

    app.config['MYSQL_DATABASE_USER'] = request.authorization.username
    app.config['MYSQL_DATABASE_PASSWORD'] = request.authorization.password
    app.config['MYSQL_DATABASE_HOST'] = request.headers.get('X-Host', '127.0.0.1')
    app.config['MYSQL_DATABASE_PORT'] = int(request.headers.get('X-Port', '3306'))

    conn = mysql.connect()
    cur = conn.cursor()
    cur.execute(SQL, records)
    conn.commit()
    cur.close()
    conn.close()
    

    if cur.rowcount == 0:
        return jsonify(status=461, message="Failed Create"), 461
    else:
        return jsonify(status=201, message="Created"), 201


##multi-valued key1=val1,key2=val2,etc update
##PATCH  /api/<db>/<table>/:id         # Update row element by primary key
#@app.route("/api/<db>/<table>/<key>", methods=['PATCH'])
#def patch_one(db=None, table=None, key=None):
#
#    assert db == request.view_args['db']
#    assert table == request.view_args['table']
#    assert key == request.view_args['key']
#
#    if not request.headers['Content-Type'] == 'application/json':
#        return jsonify(status=412, errorType="Precondition Failed"), 412
#
#    post = request.get_json()
#
#    columns=[]
#    records=[]
#    for _key in post:
#        columns.append(_key+'=?')
#        records.append(post[_key])
#
#    fields = ",".join([str(k) for k in columns])
#
#    SQL = "UPDATE "+str(db)+"."+str(table)+" SET "+str(fields)+" WHERE id='"+str(key)+"'"
#    print(SQL)
#
#    #update = insertsql(SQL, values)
#    #if update is True:
#
#    app.config['MYSQL_DATABASE_USER'] = request.authorization.username
#    app.config['MYSQL_DATABASE_PASSWORD'] = request.authorization.password
#    app.config['MYSQL_DATABASE_HOST'] = request.headers.get('X-Host', '127.0.0.1')
#    app.config['MYSQL_DATABASE_PORT'] = int(request.headers.get('X-Port', '3306'))
#
#    conn = mysql.connect()
#    cur = conn.cursor()
#    cur.execute(SQL, records)
#    conn.commit()
#    cur.close()
#    conn.close()
#
#    if cur.rowcount == 0:
#        #return jsonify(status=204, message="No Content"), 204
#        return jsonify(status=201, message="Created", update="Success"), 201
#    else:
#        return jsonify(status=465, message="Failed Update"), 465



#DELETE /api/<db>/<table>/:id         # Delete a row by primary key
@app.route("/api/<db>/<table>/<key>", methods=['DELETE'])
def delete_one(db=None, table=None, key=None):

    assert db == request.view_args['db']
    assert table == request.view_args['table']
    assert key == request.view_args['key']

    SQL = "DELETE FROM "+str(db)+"."+str(table)+" WHERE id='"+str(key)+"'"
     
    delete = commitsql(SQL)

    if delete is True:
        return jsonify(status=211, message="Deleted"), 211
    else:
        return jsonify(status=466, message="Failed Delete"), 466

#multi-valued key1=val1,key2=val2,etc update
##PATCH  /api/<db>/<table>/:id         # Update row element by primary key
#@app.route("/api/<db>/<table>/<key>", methods=['PATCH'])
#def patch_one(db=None, table=None, key=None):
#
#    assert db == request.view_args['db']
#    assert table == request.view_args['table']
#    assert key == request.view_args['key']
#
#    if not request.headers['Content-Type'] == 'application/json':
#        return jsonify(status=412, errorType="Precondition Failed"), 412
#
#    post = request.get_json()
#
#    colmns=[]
#    values=[]
#    for _key in post:
#        colmns.append(_key+'=?')
#        values.append(post[_key])
#
#    fields = ",".join([str(k) for k in colmns])
#
#    SQL = "UPDATE "+str(db)+"."+str(table)+" SET "+str(fields)+" WHERE id='"+str(key)+"'"
#    print(SQL)
#
#    update = insertsql(SQL, values)
#
#    if update is True:
#        #return jsonify(status=204, message="No Content"), 204
#        return jsonify(status=201, message="Created", update="Success"), 201
#    else:
#        return jsonify(status=465, message="Failed Update"), 465

#cur.execute("UPDATE arp SET data=? WHERE mac=?", (update, mac))
#UPDATE table_name 
#SET column1=value1,column2=value2 
#WHERE condition; 


##PATCH  /api/<db>/<table>/:id         # Update row element by primary key (single key/val)
#@app.route("/api/<db>/<table>/<key>", methods=['PATCH'])
#def patch_one(db=None, table=None, key=None):
#
#    assert db == request.view_args['db']
#    assert table == request.view_args['table']
#    assert key == request.view_args['key']
#
#    if not request.headers['Content-Type'] == 'application/json':
#        return jsonify(status=412, errorType="Precondition Failed"), 412
#
#    post = request.get_json()
#
#    if len(post) > 1:
#        return jsonify(status=405, errorType="Method Not Allowed", errorMessage="Single Key-Value Only"), 405
#
#    #colmns=[]
#    values=[]
#    for _key in post:
#        field = _key
#        values.append(post[_key])
#    #    colmns.append(_key+'=?')
#    #fields = ",".join([str(k) for k in colmns])
#
#    SQL = "UPDATE "+str(db)+"."+str(table)+" SET "+str(field)+"=? WHERE id='"+str(key)+"'"
#    print(SQL)
#    print(values)
#
#    update = insertsql(SQL, values)
#    #update = True
#
#
#    if update is True:
#        #return jsonify(status=204, message="No Content"), 204
#        return jsonify(status=201, message="Created", update="Success"), 201
#    else:
#        return jsonify(status=465, message="Failed Update"), 465

#PATCH  /api/<db>/<table>/:id         # Update row element by primary key (single key/val)
@app.route("/api/<db>/<table>/<key>", methods=['PATCH'])
def patch_one(db=None, table=None, key=None):

    assert db == request.view_args['db']
    assert table == request.view_args['table']
    assert key == request.view_args['key']

    if not request.headers['Content-Type'] == 'application/json':
        return jsonify(status=412, errorType="Precondition Failed"), 412

    post = request.get_json()

    if len(post) > 1:
        return jsonify(status=405, errorType="Method Not Allowed", errorMessage="Single Key-Value Only"), 405

    #colmns=[]
    #records=[]

    for _key in post:
        field = _key
        value = post[_key]

    #    colmns.append(_key+'=?')
    #fields = ",".join([str(k) for k in colmns])

    #SQL = "UPDATE "+str(db)+"."+str(table)+" SET "+str(field)+"=? WHERE id='"+str(key)+"'"

    SQL = "UPDATE "+str(db)+"."+str(table)+" SET "+str(field)+"='"+str(value)+"' WHERE id='"+str(key)+"'"

    #print(SQL)
    #print(records)

    #update = insertsql(SQL, values)
    #update = True


    app.config['MYSQL_DATABASE_USER'] = request.authorization.username
    app.config['MYSQL_DATABASE_PASSWORD'] = request.authorization.password
    app.config['MYSQL_DATABASE_HOST'] = request.headers.get('X-Host', '127.0.0.1')
    app.config['MYSQL_DATABASE_PORT'] = int(request.headers.get('X-Port', '3306'))

    conn = mysql.connect()
    cur = conn.cursor()
    cur.execute(SQL)
    #cur.execute(SQL, records)
    conn.commit()
    cur.close()
    conn.close()

    if cur.rowcount == 0:
        return jsonify(status=465, message="Failed Update"), 465
    else:
        return jsonify(status=201, message="Created", update="Success"), 201
    #hmmm.  this is 465 when success but nothing to update when column data and update are the same.


#PUT    /api/<db>/<table>             # Replaces existing row with new row
#cur.execute("REPLACE INTO nmap VALUES(?, DATETIME('now'), ?)", (ip, data))





@app.errorhandler(404)
def not_found(error=None):
    message = { 'status': 404, 'errorType': 'Not Found: ' + request.url }
    return jsonify(message), 404


@app.errorhandler(Exception)
def handle_exception(e):

    print(str(type(e)))
    print(str(e))

    if isinstance(e, HTTPException):
        return jsonify(status=e.code, errorType="HTTP Exception", errorMessage=str(e)), e.code

    #if isinstance(e, OperationalError):
    #    return jsonify(status=512, errorType="OperationalError", errorMessage=str(e)), 512
    #print(type(e).__name__)
    if type(e).__name__ == 'OperationalError':
        return jsonify(status=512, errorType="OperationalError", errorMessage=str(e)), 512

    res = {'status': 500, 'errorType': 'Internal Server Error'}
    res['errorMessage'] = str(e)
    return jsonify(res), 500

#<class 'pymysql.err.OperationalError'>
#(1054, "Unknown column 'descriptionXXXXX' in 'field list'")



#def Conf(f):
#    @wraps(f)
#    def decorated(*args, **kwargs):
#        #app.config['MYSQL_DATABASE_USER'] = request.authorization.username
#        #app.config['MYSQL_DATABASE_PASSWORD'] = request.authorization.password
#        #app.config['MYSQL_DATABASE_HOST'] = request.headers.get('X-Host', '127.0.0.1')
#        #app.config['MYSQL_DATABASE_PORT'] = int(request.headers.get('X-Port', '3306'))
#        #if not request.authorization:
#        #    print('no request.authorization')
#        #    return jsonify(status=401,errorType="Unauthorized",errorMessage="Requires BasicAuth"), 401
#
#        #db = mysql.connector.connect
#
#        config = {
#        'user': request.authorization.username,
#        'password': request.authorization.password,
#        'database': '',
#        'host': request.headers.get('X-Host', '127.0.0.1'),
#        'port': int(request.headers.get('X-Port', '3306')),
#        'raise_on_warnings': True,
#        'auth_plugin': 'mysql_native_password',
#        }
#
#        return f(*args, **kwargs)
#    return decorated


#@Conf
def fetchall(sql):
    #print(config)
    cnx = sqlConnection()
    #cnx = mysql.connector.connect(**config)
    #conn = mysql.connect()
    #cur = conn.cursor()
    cur = cnx.cursor(buffered=True)
    cur.execute(sql)
    rows = cur.fetchall()
    cur.close()
    #conn.close()
    cnx.close()
    return rows

#@Conf
def fetchone(sql):
    sqlConnection()
    db = mysql.connect()
    cur = conn.cursor()
    cur.execute(sql)
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row

#@Conf
def insertsql(sql, values):
    conn = mysql.connect()
    cur = conn.cursor()
    cur.execute(sql, values)
    conn.commit()
    print(str(cur.rowcount))
    if cur.rowcount == 0:
        cur.close()
        conn.close()
        return False
    cur.close()
    conn.close()
    return True

#@Conf
def commitsql(sql):
    conn = mysql.connect()
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    cur.close()
    conn.close()
    if cur.rowcount == 0:
        return False
    else:
        return True





if __name__ == "__main__":
    app.run(port=8980, debug=False)


