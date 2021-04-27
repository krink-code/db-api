
# python3

__version__='0.0.1.dev.20210426-1'

from app import app
from flask import request
from flask import jsonify
from werkzeug.exceptions import HTTPException
from db import mysql
import cryptography


@app.route("/", methods=['GET'])
def root():
    return jsonify(status=200, message="OK", version=__version__), 200


@app.route("/api", methods=['GET'])
def show_databases():
    SQL = 'SHOW DATABASES'
    rows = fetchall(SQL)
    List=[]
    for row in rows:
        List.append(row)
    return jsonify(List), 200


@app.route("/api/<db>", methods=['GET'])
def show_tables(db=None):
    assert db == request.view_args['db']
    SQL = 'SHOW TABLES FROM ' + str(db)
    rows = fetchall(SQL)
    return jsonify(rows), 200


@app.route("/api/<db>/<table>", methods=['GET'])
def api(db=None, table=None):

    assert db == request.view_args['db']
    assert table == request.view_args['table']

    fields = request.args.get("fields", None)
    limit  = request.args.get("limit", None)

    if not request.query_string:
        SQL = 'SHOW FIELDS FROM ' + str(db) +'.'+ str(table)
        rows = fetchall(SQL)
        return jsonify(rows), 200

    if not fields:
        fields = '*'

    SQL = 'SELECT '+ str(fields) +' FROM '+ str(db) +'.'+ str(table) 

    if limit:
        SQL += ' LIMIT ' + str(limit)

    #rows = fetchall(SQL)

    #return jsonify(rows), 200
    #return jsonify([rows.to_json() for row in rows]), 200

    username = request.authorization.username
    password = request.authorization.password
    dbhost   = request.headers.get('X-Host', '127.0.0.1')
    dbport   = request.headers.get('X-Port', '3306')

    app.config['MYSQL_DATABASE_USER'] = username
    app.config['MYSQL_DATABASE_PASSWORD'] = password
    app.config['MYSQL_DATABASE_HOST'] = dbhost
    app.config['MYSQL_DATABASE_PORT'] = int(dbport)

    conn = mysql.connect()
    cur = conn.cursor()
    cur.execute(SQL)
    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    cur.close()
    conn.close()

    result = []
    for row in rows:
        row = dict(zip(columns, row))
        result.append(row)

    #return jsonify(result), 200

    import json
    json_response=json.dumps(result)
    response=Response(json_response,content_type='application/json; charset=utf-8')
    response.headers.add('content-length',len(json_response))
    response.status_code=200
    return response, 200




@app.errorhandler(404)
def not_found(error=None):
    message = { 'status': 404, 'message': 'Not Found: ' + request.url }
    return jsonify(message), 404


@app.errorhandler(Exception)
def handle_exception(e):
    if isinstance(e, HTTPException):
        return e
    res = {'status': 500, 'errorType': 'Internal Server Error'}
    res['errorMessage'] = str(e)
    return jsonify(res), 500


def fetchall(sql):
    username = request.authorization.username
    password = request.authorization.password
    dbhost   = request.headers.get('X-Host', '127.0.0.1')
    dbport   = request.headers.get('X-Port', '3306')

    app.config['MYSQL_DATABASE_USER'] = username
    app.config['MYSQL_DATABASE_PASSWORD'] = password
    app.config['MYSQL_DATABASE_HOST'] = dbhost
    app.config['MYSQL_DATABASE_PORT'] = int(dbport)

    conn = mysql.connect()
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


if __name__ == "__main__":
    app.run(port=8980, debug=False)


