
# -*- coding: utf-8 -*-

__version__='1.0.1'

from flask import Flask

from flask import request
from flask import jsonify
from werkzeug.exceptions import HTTPException

from flask_cors import CORS

import mysql.connector

app = Flask(__name__)
CORS(app)

app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True    #default False
app.config['JSON_SORT_KEYS'] = True                 #default True
app.config['JSONIFY_MIMETYPE'] = 'application/json' #default 'application/json'


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
#GET    /api/<db>/<table>?query=true  # List rows of table. fields=id,name&limit=2,5
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

    if rows:
        return jsonify(rows), 200
    else:
        return jsonify(status=404, message="Not Found"), 404


#GET    /api/<db>/<table>/:id         # Retrieve a row by primary key
#GET    /api/<db>/<table>/:id?fields= # fields=&column=
@app.route("/api/<db>/<table>/<key>", methods=['GET'])
def get_one(db=None, table=None, key=None):

    assert db == request.view_args['db']
    assert table == request.view_args['table']
    assert key == request.view_args['key']

    fields = request.args.get("fields", '*')
    column = request.args.get("column", 'id')

    SQL = "SELECT "+ str(fields) +" FROM "+ str(db) +"."+ str(table) +" WHERE "+str(column)+"='"+str(key)+"'"

    row = fetchone(SQL)

    if row:
        return jsonify(row), 200
    else:
        return jsonify(status=404, message="Not Found"), 404


#POST   /api/<db>/<table>             # Create a new row
#                                     # key1=val1,key2=val2
@app.route("/api/<db>/<table>", methods=['POST'])
def post_insert(db=None, table=None):

    assert db == request.view_args['db']
    assert table == request.view_args['table']

    if not request.headers['Content-Type'] == 'application/json':
        return jsonify(status=412, errorType="Precondition Failed"), 412

    post = request.get_json()

    placeholders = ['%s'] * len(post)

    fields = ",".join([str(key) for key in post])
    places = ",".join([str(key) for key in placeholders])

    records=[]
    for key in post:
        records.append(post[key])

    SQL = "INSERT INTO " +str(db)+"."+str(table)+" ("+str(fields)+") VALUES ("+str(places)+")"

    insert = sqlexec(SQL, records)

    if insert > 0:
        return jsonify(status=201, message="Created", insert=True), 201
    else:
        return jsonify(status=461, message="Failed Create", insert=False), 461


#DELETE /api/<db>/<table>/:id         # Delete a row by primary key
#DELETE /api/<db>/<table>/:id?column= # column=
@app.route("/api/<db>/<table>/<key>", methods=['DELETE'])
def delete_one(db=None, table=None, key=None):

    assert db == request.view_args['db']
    assert table == request.view_args['table']
    assert key == request.view_args['key']

    column = request.args.get("column", 'id')

    SQL = "DELETE FROM "+str(db)+"."+str(table)+" WHERE "+str(column)+"='"+str(key)+"'"

    delete = sqlcommit(SQL)

    if delete > 0:
        return jsonify(status=211, message="Deleted", delete=True), 211
    else:
        return jsonify(status=466, message="Failed Delete", delete=False), 466


#PATCH  /api/<db>/<table>/:id         # Update row element by primary key (single key/val)
#PATCH  /api/<db>/<table>/:id?column= # column=
@app.route("/api/<db>/<table>/<key>", methods=['PATCH'])
def patch_one(db=None, table=None, key=None):

    assert db == request.view_args['db']
    assert table == request.view_args['table']
    assert key == request.view_args['key']

    column = request.args.get("column", 'id')

    if not request.headers['Content-Type'] == 'application/json':
        return jsonify(status=412, errorType="Precondition Failed"), 412

    post = request.get_json()

    if len(post) > 1:
        return jsonify(status=405, errorType="Method Not Allowed", errorMessage="Single Key-Value Only", update=False), 405

    for _key in post:
        field = _key
        value = post[_key]

    SQL = "UPDATE "+str(db)+"."+str(table)+" SET "+str(field)+"='"+str(value)+"' WHERE "+str(column)+"='"+str(key)+"'"

    update = sqlcommit(SQL)

    if update > 0:
        #return jsonify(status=204, message="No Content"), 204
        return jsonify(status=201, message="Created", update=True), 201
    else:
        return jsonify(status=465, message="Failed Update", update=False), 465


#PUT    /api/<db>/<table>             # Replace existing row with new row
#                                     # key1=val1,key2=val2
@app.route("/api/<db>/<table>", methods=['PUT'])
def put_replace(db=None, table=None):

    assert db == request.view_args['db']
    assert table == request.view_args['table']

    if not request.headers['Content-Type'] == 'application/json':
        return jsonify(status=412, errorType="Precondition Failed"), 412

    post = request.get_json()

    placeholders = ['%s'] * len(post)

    fields = ",".join([str(key) for key in post])
    places = ",".join([str(key) for key in placeholders])

    records=[]
    for key in post:
        records.append(post[key])

    SQL = "REPLACE INTO " +str(db)+"."+str(table)+" ("+str(fields)+") VALUES ("+str(places)+")"

    replace = sqlexec(SQL, records)

    if replace > 0:
        return jsonify(status=201, message="Created", replace=True), 201
    else:
        return jsonify(status=461, message="Failed Create", replace=False), 461



@app.errorhandler(404)
def not_found(error=None):
    message = { 'status': 404, 'errorType': 'Not Found: ' + request.url }
    return jsonify(message), 404


@app.errorhandler(Exception)
def handle_exception(e):

    if isinstance(e, HTTPException):
        return jsonify(status=e.code, errorType="HTTP Exception", errorMessage=str(e)), e.code

    if type(e).__name__ == 'OperationalError':
        return jsonify(status=512, errorType="OperationalError", errorMessage=str(e)), 512

    if type(e).__name__ == 'InterfaceError':
        return jsonify(status=512, errorType="InterfaceError", errorMessage=str(e)), 512

    if type(e).__name__ == 'ProgrammingError':
        return jsonify(status=512, errorType="ProgrammingError", errorMessage=str(e)), 512

    if type(e).__name__ == 'AttributeError':
        return jsonify(status=512, errorType="AttributeError", errorMessage=str(e)), 512

    res = {'status': 500, 'errorType': 'Internal Server Error'}
    res['errorMessage'] = str(e)
    return jsonify(res), 500


def fetchall(sql):
    cnx = sqlConnection()
    cur = cnx.cursor(buffered=True)
    cur.execute(sql)
    rows = cur.fetchall()
    cur.close()
    cnx.close()
    return rows

def fetchone(sql):
    cnx = sqlConnection()
    cur = cnx.cursor(buffered=True)
    cur.execute(sql)
    row = cur.fetchone()
    cur.close()
    cnx.close()
    return row

def sqlexec(sql, values):
    cnx = sqlConnection()
    cur = cnx.cursor(buffered=True)
    cur.execute(sql, values)
    cnx.commit()
    rowcount = cur.rowcount
    cur.close()
    cnx.close()
    return rowcount

def sqlcommit(sql):
    cnx = sqlConnection()
    cur = cnx.cursor(buffered=True)
    cur.execute(sql)
    cnx.commit()
    rowcount = cur.rowcount
    cur.close()
    cnx.close()
    return rowcount

def sqlConnection():
    config = {
        'user':                   request.authorization.username,
        'password':               request.authorization.password,
        'host':                   request.headers.get('X-Host', '127.0.0.1'),
        'port':               int(request.headers.get('X-Port', '3306')),
        'database':               request.headers.get('X-Db', ''),
        'raise_on_warnings':      request.headers.get('X-Raise-Warnings', True),
        'get_warnings':           request.headers.get('X-Get-Warnings', True),
        'auth_plugin':            request.headers.get('X-Auth-Plugin', 'mysql_native_password'),
        'use_pure':               request.headers.get('X-Pure', True),
        'use_unicode':            request.headers.get('X-Unicode', True),
        'charset':                request.headers.get('X-Charset', 'utf8'),
        'connection_timeout': int(request.headers.get('X-Connection-Timeout', 60)),
    }
    db = mysql.connector.connect(**config)
    return db



def main():
    app.run(port=8980, debug=False)    


if __name__ == "__main__":
    main()


