
# -*- coding: utf-8 -*-

"""server: db-api."""

from __future__ import absolute_import

__version__ = '1.0.5'

import base64
import decimal
import json

import flask.json
from flask import Flask
from flask import request
from flask import jsonify
from werkzeug.exceptions import HTTPException
from flask_cors import CORS

import mysql.connector


class AppJSONEncoder(flask.json.JSONEncoder):
    """app: json encoder."""

    def default(self, o):
        """default: self."""
        if isinstance(o, decimal.Decimal):
            # Convert decimal instance to string
            return str(o)

        if isinstance(o, bytes):
            # Convert bytes instance to string, json
            try:
                o = o.decode('utf-8')
                try:
                    o = json.loads(o)
                    return o
                except json.decoder.JSONDecodeError:
                    return str(o)

            except UnicodeDecodeError:
                return str(o)

        if isinstance(o, bytearray):
            # Convert bytearray instance to string
            o = o.decode('utf-8')
            return str(o)

        return super().default(o)


APP = Flask(__name__)
CORS(APP, support_credentials=True)

APP.json_encoder = AppJSONEncoder
APP.config['JSONIFY_PRETTYPRINT_REGULAR'] = True     # default False
APP.config['JSON_SORT_KEYS'] = False                 # default True
APP.config['JSONIFY_MIMETYPE'] = 'application/json'  # default 'application/json'


@APP.route("/", methods=['GET'])
def root():
    """GET: Show Status."""
    return jsonify(status=200, message="OK", version=__version__), 200


@APP.route("/api", methods=['GET'])
def show_databases():
    """GET: /api Show Databases."""
    sql = "SHOW DATABASES"
    rows = fetchall(sql)
    return jsonify(rows), 200


@APP.route("/api/<database>", methods=['GET'])
def show_tables(database=None):
    """GET: /api/<database> Show Database Tables."""
    database = request.view_args['database']
    sql = "SHOW TABLES FROM " + database
    rows = fetchall(sql)
    return jsonify(rows), 200


@APP.route("/api/<database>/<table>", methods=['GET'])
def get_many(database=None, table=None):
    """GET: /api/<database>/<table> Show Database Table fields."""
    # ?query=true List rows of table. fields=id,name&limit=2,5
    database = request.view_args['database']
    table = request.view_args['table']

    fields = request.args.get("fields", '*')
    limit = request.args.get("limit", None)

    if not request.query_string:
        sql = "SHOW FIELDS FROM " + database + "." + table
    else:
        sql = "SELECT " + fields + " FROM " + database + "." + table

    if limit:
        sql += " LIMIT " + limit

    rows = fetchall(sql)

    if rows:
        return jsonify(rows), 200

    return jsonify(status=404, message="Not Found"), 404


@APP.route("/api/<database>/<table>/<key>", methods=['GET'])
def get_one(database=None, table=None, key=None):
    """GET: /api/<database>/<table>:id."""
    # Retrieve a row by primary key. id?fields= fields=&column=
    database = request.view_args['database']
    table = request.view_args['table']
    key = request.view_args['key']

    fields = request.args.get("fields", '*')
    column = request.args.get("column", 'id')

    sql = "SELECT " + fields + " FROM " + database + "." + table
    sql += " WHERE " + column + "='" + key + "'"

    row = fetchone(sql)

    if row:
        return jsonify(row), 200

    return jsonify(status=404, message="Not Found"), 404


@APP.route("/api", methods=['POST'])
def post_api():
    """POST: /api."""
    if request.is_json:
        return jsonify(status=415, post='json'), 415

    if request.form:
        return jsonify(status=415, post='form'), 415

    if request.files:
        return jsonify(status=415, post='files'), 415

    if request.stream:

        if request.content_type == 'image/jpg':
            return jsonify(status=415, post='stream', content_type='image/jpg'), 415

        if request.content_type == 'application/octet-stream':
            return jsonify(status=415,
                           post='stream',
                           content_type='application/octet-stream'), 415

        if str(request.content_type).lower().startswith('text/plain'):
            return jsonify(status=415, post='stream', content_type='text/plain'), 415

        if str(request.content_type).lower().startswith('text/sql'):
            return post_sql()

        return jsonify(status=415, post='stream'), 415

    return jsonify(status=415,
                   error='Unsupported Media Type',
                   method='POST'), 415


@APP.route("/api/<database>/<table>", methods=['POST'])
def post_insert(database=None, table=None):
    """POST: /api/<database>/<table>."""
    # Create a new row. key1=val1,key2=val2.
    database = request.view_args['database']
    table = request.view_args['table']

    if request.is_json:
        return post_json(database, table)

    if request.form:
        return post_form(database, table)

    _return = {'status': 417,
               'message': 'Expectation Failed',
               'details': 'Can Not Meet Expectation: request-header field',
               'method': 'POST',
               'insert': False}
    return jsonify(_return), 417


@APP.route("/api/<database>/<table>/<key>", methods=['DELETE'])
def delete_one(database=None, table=None, key=None):
    """DELETE: /api/<database>/<table>:id."""
    # Delete a row by primary key id?column=
    database = request.view_args['database']
    table = request.view_args['table']
    key = request.view_args['key']

    column = request.args.get("column", 'id')

    sql = "DELETE FROM " + database + "." + table
    sql += " WHERE " + column + "='" + key + "'"

    delete = sqlcommit(sql)

    if delete > 0:
        return jsonify(status=211, message="Deleted", delete=True), 211

    return jsonify(status=466, message="Failed Delete", delete=False), 466


@APP.route("/api/<database>/<table>/<key>", methods=['PATCH'])
def patch_one(database=None, table=None, key=None):
    """PATCH: /api/<database>/<table>:id."""
    # Update row element by primary key (single key/val) id?column=
    database = request.view_args['database']
    table = request.view_args['table']
    key = request.view_args['key']

    column = request.args.get("column", 'id')

    if not request.headers['Content-Type'] == 'application/json':
        return jsonify(status=412, errorType="Precondition Failed"), 412

    post = request.get_json()

    if len(post) > 1:
        _return = {'status': 405,
                   'errorType': 'Method Not Allowed',
                   'errorMessage': 'Single Key-Value Only',
                   'update': False}
        return jsonify(_return), 405

    for _key in post:
        field = _key
        value = post[_key]

    sql = "UPDATE " + database + "." + table
    sql += " SET " + field + "='" + value + "' WHERE " + column + "='" + key + "'"

    update = sqlcommit(sql)

    if update > 0:
        return jsonify(status=201, message="Created", update=True), 201

    return jsonify(status=465, message="Failed Update", update=False), 465


@APP.route("/api/<database>/<table>", methods=['PUT'])
def put_replace(database=None, table=None):
    """PUT: /api/<database>/<table>."""
    # Replace existing row with new row. key1=val1,key2=val2."""
    database = request.view_args['database']
    table = request.view_args['table']

    if not request.headers['Content-Type'] == 'application/json':
        return jsonify(status=412, errorType="Precondition Failed"), 412

    post = request.get_json()

    placeholders = ['%s'] * len(post)

    fields = ",".join([str(key) for key in post])
    places = ",".join([str(key) for key in placeholders])

    records = []
    for key in post:
        records.append(post[key])

    sql = "REPLACE INTO " + database + "." + table
    sql += " (" + fields + ") VALUES (" + places + ")"

    replace = sqlexec(sql, records)

    if replace > 0:
        return jsonify(status=201,
                       message="Created",
                       replace=True,
                       rowid=replace), 201

    return jsonify(status=461, message="Failed Create", replace=False), 461


@APP.errorhandler(404)
def not_found(_e=None):
    """Not_Found: HTTP File Not Found 404."""
    message = {'status': 404, 'errorType': 'Not Found: ' + request.url}
    return jsonify(message), 404


@APP.errorhandler(Exception)
def handle_exception(_e):
    """Exception: HTTP Exception."""
    if isinstance(_e, HTTPException):
        return jsonify(status=_e.code,
                       errorType="HTTP Exception",
                       errorMessage=str(_e)), _e.code

    if type(_e).__name__ == 'OperationalError':
        return jsonify(status=512,
                       errorType="OperationalError",
                       errorMessage=str(_e)), 512

    if type(_e).__name__ == 'InterfaceError':
        return jsonify(status=512,
                       errorType="InterfaceError",
                       errorMessage=str(_e)), 512

    if type(_e).__name__ == 'ProgrammingError':
        return jsonify(status=512,
                       errorType="ProgrammingError",
                       errorMessage=str(_e)), 512

    if type(_e).__name__ == 'AttributeError':
        return jsonify(status=512,
                       errorType="AttributeError",
                       errorMessage=str(_e)), 512

    res = {'status': 500, 'errorType': 'Internal Server Error'}
    res['errorMessage'] = str(_e)
    return jsonify(res), 500


def post_sql():
    """post: sql."""
    post = request.data
    sql = post.decode('utf-8')

    cnx = sql_connection()
    cur = cnx.cursor(buffered=True)

    try:
        for result in cur.execute(sql, multi=True):

            if result.with_rows:
                return jsonify(result.fetchall()), 200

            cnx.commit()
            return jsonify(status=201,
                           statment=result.statement,
                           rowcount=result.rowcount,
                           lastrowid=result.lastrowid), 201
    finally:
        cur.close()
        cnx.close()

    return jsonify(status=202, method='POST'), 202


def post_json(database, table):
    """post: json data application/json."""
    post = request.get_json()

    placeholders = ['%s'] * len(post)

    fields = ",".join([str(key) for key in post])
    places = ",".join([str(key) for key in placeholders])

    records = []
    for key in post:
        records.append(post[key])

    sql = "INSERT INTO " + database + "." + table
    sql += " (" + fields + ") VALUES (" + places + ")"

    insert = sqlexec(sql, records)

    if insert > 0:
        return jsonify(status=201,
                       message="Created",
                       insert=True,
                       rowid=insert), 201

    return jsonify(status=461, message="Failed Create", insert=False), 461


def post_form(database, table):
    """post: form data application/x-www-form-urlencoded."""
    credentials = request.form.get('credentials', None)

    if credentials:

        columns = []
        records = []
        for key in request.form.keys():
            if key == 'credentials':
                continue
            columns.append(key)
            records.append(request.form[key])

        count = len(request.form) - 1
        placeholders = ['%s'] * count

        places = ",".join([str(key) for key in placeholders])

        fields = ",".join([str(key) for key in columns])

        base64_user, base64_pass = base64_untoken(credentials.encode('ascii'))

        sql = "INSERT INTO " + database + "." + table
        sql += " (" + fields + ") VALUES (" + places + ")"

        insert = sqlinsert(sql, records, base64_user, base64_pass)

        if insert > 0:
            return jsonify(status=201,
                           message="Created",
                           method="POST",
                           insert=True,
                           rowid=insert), 201

        return jsonify(status=461,
                       message="Failed Create",
                       method="POST",
                       insert=False), 461

    return jsonify(status=401,
                   message='Unauthorized',
                   details='No valid authentication credentials for target resource',
                   method='POST',
                   insert=False), 401


def base64_untoken(base64_bytes):
    """base64: untoken."""
    token_bytes = base64.b64decode(base64_bytes)
    untoken = token_bytes.decode('ascii')
    base64_user = untoken.split(":", 1)[0]
    base64_pass = untoken.split(":", 1)[1]
    return base64_user, base64_pass


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
    lastrowid = cur.lastrowid
    cur.close()
    cnx.close()
    return lastrowid


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
    lastrowid = cur.lastrowid
    cur.close()
    cnx.close()
    return lastrowid


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
        'connection_timeout': int(request.headers.get('X-Connection-Timeout', 10)),
    }
    _db = mysql.connector.connect(**config)
    return _db


def main():
    """main: app."""
    APP.run(port=8980, debug=False)


if __name__ == "__main__":
    main()
