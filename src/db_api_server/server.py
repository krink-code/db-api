
# -*- coding: utf-8 -*-

"""server: db-api."""

from __future__ import absolute_import

__version__ = '1.0.4-0-20211120-2'

import base64
import decimal
import json

import flask.json
from flask import Flask
from flask import request
from flask import jsonify
from flask.logging import create_logger
from werkzeug.exceptions import HTTPException
from flask_cors import CORS

import mysql.connector

class AppJSONEncoder(flask.json.JSONEncoder):

    """app: json encoder."""
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            # Convert decimal instance to string.
            return str(obj)
        if isinstance(obj, bytes):
            # Convert bytes instance to string, json.
            try:
                obj = obj.decode('utf-8')
                try:
                    obj = json.loads(obj)
                    return obj
                except json.decoder.JSONDecodeError:
                    return str(obj)
            except UnicodeDecodeError:
                return str(obj)
        return super(AppJSONEncoder, self).default(obj)


APP = Flask(__name__)
CORS(APP, support_credentials=True)
APP.logger = create_logger(APP)
APP.json_encoder = AppJSONEncoder
APP.config['JSONIFY_PRETTYPRINT_REGULAR'] = True    #default False
APP.config['JSON_SORT_KEYS'] = True                 #default True
APP.config['JSONIFY_MIMETYPE'] = 'application/json' #default 'application/json'

@APP.route("/", methods=['GET'])
def root():
    """GET: Show Status."""
    return jsonify(status=200, message="OK", version=__version__), 200


@APP.route("/api", methods=['GET'])
def show_databases():
    """GET: /api Show Databases."""
    sql = 'SHOW DATABASES'
    rows = fetchall(sql)
    return jsonify(rows), 200


@APP.route("/api/<db>", methods=['GET'])
def show_tables(db=None):
    """GET: /api/<db> Show Database Tables."""
    db == request.view_args['db']
    sql = 'SHOW TABLES FROM ' + str(db)
    rows = fetchall(sql)
    return jsonify(rows), 200


@APP.route("/api/<db>/<table>", methods=['GET'])
def get_many(db=None, table=None):
    """GET: /api/<db>/<table> Show Database Table fields
       GET: /api/<db>/<table>?query=true List rows of table. fields=id,name&limit=2,5."""

    db == request.view_args['db']
    table == request.view_args['table']

    fields = request.args.get("fields", '*')
    limit = request.args.get("limit", None)

    if not request.query_string:
        sql = 'SHOW FIELDS FROM ' + str(db) +'.'+ str(table)
    else:
        sql = 'SELECT '+ str(fields) +' FROM '+ str(db) +'.'+ str(table)

    if limit:
        sql += ' LIMIT ' + str(limit)

    rows = fetchall(sql)

    if rows:
        return jsonify(rows), 200
    else:
        return jsonify(status=404, message="Not Found"), 404


@APP.route("/api/<db>/<table>/<key>", methods=['GET'])
def get_one(db=None, table=None, key=None):
    """GET: /api/<db>/<table>:id Retrieve a row by primary key
       GET: /api/<db>/<table>/:id?fields= fields=&column=."""

    db == request.view_args['db']
    table == request.view_args['table']
    key == request.view_args['key']

    fields = request.args.get("fields", '*')
    column = request.args.get("column", 'id')

    sql = "SELECT "+ str(fields) +" FROM "+ str(db) +"."+ str(table) +" WHERE "+str(column)+"='"+str(key)+"'"

    row = fetchone(sql)

    if row:
        return jsonify(row), 200
    else:
        return jsonify(status=404, message="Not Found"), 404


@APP.route("/api/<db>/<table>", methods=['POST'])
def post_insert(db=None, table=None):
    """POST: /api/<db>/<table> Create a new row
                               key1=val1,key2=val2."""

    db == request.view_args['db']
    table == request.view_args['table']

    if request.is_json:

        post = request.get_json()

        placeholders = ['%s'] * len(post)

        fields = ",".join([str(key) for key in post])
        places = ",".join([str(key) for key in placeholders])

        records=[]
        for key in post:
            records.append(post[key])

        sql = "INSERT INTO " +str(db)+"."+str(table)+" ("+str(fields)+") VALUES ("+str(places)+")"

        insert = sqlexec(sql, records)

        if insert > 0:
            return jsonify(status=201, message="Created", insert=True), 201
        else:
            return jsonify(status=461, message="Failed Create", insert=False), 461

    elif request.form:

        credentials = request.form.get('credentials', None)

        if credentials:

            columns=[]
            records=[]
            for key in request.form.keys():
                if key == 'credentials':
                    continue
                columns.append(key)
                records.append(request.form[key])

            count = len(request.form) - 1
            placeholders = ['%s'] * count

            places = ",".join([str(key) for key in placeholders])

            fields = ",".join([str(key) for key in columns])

            base64_bytes = credentials.encode('ascii')
            token_bytes = base64.b64decode(base64_bytes)
            untoken = token_bytes.decode('ascii')

            base64_user = untoken.split(":", 1)[0]
            base64_pass = untoken.split(":", 1)[1]

            sql = "INSERT INTO " +str(db)+"."+str(table)+" ("+str(fields)+") VALUES ("+str(places)+")"

            insert = sqlinsert(sql, records, base64_user, base64_pass)

            if insert > 0:
                return jsonify(status=201, message="Created", method="POST", insert=True), 201
            else:
                return jsonify(status=461, message="Failed Create", method="POST", insert=False), 461

        return jsonify(status=401, message="Unauthorized", details="No valid authentication credentials for the target resource", method="POST", insert=False), 401

    else:

        return jsonify(status=417, message="Expectation Failed", details="The server cannot meet the requirements of the Expect request-header field", method="POST", insert=False), 417


@APP.route("/api/<db>/<table>/<key>", methods=['DELETE'])
def delete_one(db=None, table=None, key=None):
    """DELETE: /api/<db>/<table>:id Delete a row by primary key
       DELETE: /api/<db>/<table>/:id?column=."""

    db == request.view_args['db']
    table == request.view_args['table']
    key == request.view_args['key']

    column = request.args.get("column", 'id')

    sql = "DELETE FROM "+str(db)+"."+str(table)+" WHERE "+str(column)+"='"+str(key)+"'"

    delete = sqlcommit(sql)

    if delete > 0:
        return jsonify(status=211, message="Deleted", delete=True), 211
    else:
        return jsonify(status=466, message="Failed Delete", delete=False), 466


@APP.route("/api/<db>/<table>/<key>", methods=['PATCH'])
def patch_one(db=None, table=None, key=None):
    """PATCH: /api/<db>/<table>:id Update row element by primary key (single key/val)
       PATCH: /api/<db>/<table>/:id?column=."""

    db == request.view_args['db']
    table == request.view_args['table']
    key == request.view_args['key']

    column = request.args.get("column", 'id')

    if not request.headers['Content-Type'] == 'application/json':
        return jsonify(status=412, errorType="Precondition Failed"), 412

    post = request.get_json()

    if len(post) > 1:
        return jsonify(status=405, errorType="Method Not Allowed", errorMessage="Single Key-Value Only", update=False), 405

    for _key in post:
        field = _key
        value = post[_key]

    sql = "UPDATE "+str(db)+"."+str(table)+" SET "+str(field)+"='"+str(value)+"' WHERE "+str(column)+"='"+str(key)+"'"

    update = sqlcommit(sql)

    if update > 0:
        #return jsonify(status=204, message="No Content"), 204
        return jsonify(status=201, message="Created", update=True), 201
    else:
        return jsonify(status=465, message="Failed Update", update=False), 465


@APP.route("/api/<db>/<table>", methods=['PUT'])
def put_replace(db=None, table=None):
    """PUT: /api/<db>/<table> Replace existing row with new row
                              key1=val1,key2=val2."""

    db == request.view_args['db']
    table == request.view_args['table']

    if not request.headers['Content-Type'] == 'application/json':
        return jsonify(status=412, errorType="Precondition Failed"), 412

    post = request.get_json()

    placeholders = ['%s'] * len(post)

    fields = ",".join([str(key) for key in post])
    places = ",".join([str(key) for key in placeholders])

    records=[]
    for key in post:
        records.append(post[key])

    sql = "REPLACE INTO " +str(db)+"."+str(table)+" ("+str(fields)+") VALUES ("+str(places)+")"

    replace = sqlexec(sql, records)

    if replace > 0:
        return jsonify(status=201, message="Created", replace=True), 201
    else:
        return jsonify(status=461, message="Failed Create", replace=False), 461


@APP.errorhandler(404)
def not_found(_e=None):
    """Not_Found: HTTP File Not Found 404."""
    message = { 'status': 404, 'errorType': 'Not Found: ' + request.url }
    return jsonify(message), 404


@APP.errorhandler(Exception)
def handle_exception(_e):
    """Exception: HTTP Exception."""
    if isinstance(_e, HTTPException):
        return jsonify(status=_e.code, errorType="HTTP Exception", errorMessage=str(_e)), _e.code

    if type(_e).__name__ == 'OperationalError':
        return jsonify(status=512, errorType="OperationalError", errorMessage=str(_e)), 512

    if type(_e).__name__ == 'InterfaceError':
        return jsonify(status=512, errorType="InterfaceError", errorMessage=str(_e)), 512

    if type(_e).__name__ == 'ProgrammingError':
        return jsonify(status=512, errorType="ProgrammingError", errorMessage=str(_e)), 512

    if type(_e).__name__ == 'AttributeError':
        return jsonify(status=512, errorType="AttributeError", errorMessage=str(_e)), 512

    res = {'status': 500, 'errorType': 'Internal Server Error'}
    res['errorMessage'] = str(_e)
    return jsonify(res), 500


def fetchall(sql):
    """sql: fetchall."""
    cnx = sql_connection()
    cur = cnx.cursor(buffered=True)
    cur.execute(sql)
    rows = cur.fetchall()
    cur.close()
    cnx.close()
    return rows


def fetchone(sql):
    """sql: fetchone."""
    cnx = sql_connection()
    cur = cnx.cursor(buffered=True)
    cur.execute(sql)
    row = cur.fetchone()
    cur.close()
    cnx.close()
    return row


def sqlexec(sql, values):
    """sql: exec values."""
    cnx = sql_connection()
    cur = cnx.cursor(buffered=True)
    cur.execute(sql, values)
    cnx.commit()
    rowcount = cur.rowcount
    cur.close()
    cnx.close()
    return rowcount


def sqlcommit(sql):
    """sql: commit."""
    cnx = sql_connection()
    cur = cnx.cursor(buffered=True)
    cur.execute(sql)
    cnx.commit()
    rowcount = cur.rowcount
    cur.close()
    cnx.close()
    return rowcount


def sqlinsert(sql, values, user, password):
    """sql: insert values, user, password."""
    cnx = sql_connection(user, password)
    cur = cnx.cursor(buffered=True)
    cur.execute(sql, values)
    cnx.commit()
    rowcount = cur.rowcount
    cur.close()
    cnx.close()
    return rowcount


def sql_connection(user=None, password=None):
    """sql: connection."""
    if not user:
        user = request.authorization.username

    if not password:
        password = request.authorization.password

    config = {
        'user':                   user,
        'password':               password,
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
    """main: app."""
    APP.run(port=8980, debug=False)


if __name__ == "__main__":
    main()
