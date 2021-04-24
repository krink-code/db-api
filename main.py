
# python3

__version__='0.0.0-3'

from app import app
from flask import request
from flask import jsonify
from werkzeug.exceptions import HTTPException
from db import mysql
import cryptography

@app.route("/", methods=['GET'])
def root():
    return jsonify(status=200, message="OK", version=__version__), 200


#@app.route("/api", methods=['GET'])
#def show_databases():
#
#    username = request.authorization.username
#    password = request.authorization.password
#    dbhost   = request.headers.get('X-Host', '127.0.0.1')
#    dbport   = request.headers.get('X-Port', '3306')
#
#    app.config['MYSQL_DATABASE_USER'] = username
#    app.config['MYSQL_DATABASE_PASSWORD'] = password
#    app.config['MYSQL_DATABASE_HOST'] = dbhost
#    app.config['MYSQL_DATABASE_PORT'] = int(dbport)
#
#    SQL = 'SHOW DATABASES' 
#
#    conn = mysql.connect()
#    cur = conn.cursor()
#    cur.execute(SQL)
#    rows = cur.fetchall()
#    cur.close()
#    conn.close()
#
#    List=[]
#    for row in rows:
#        List.append(row)
#    resp = jsonify(List)
#    return resp, 200

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
    #List=[]
    #for row in rows:
    #    List.append(row)
    #return jsonify(List), 200
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

    rows = fetchall(SQL)
    return jsonify(rows), 200

    #D={}
    #c=0
    #for row in rows:
    #    c+=1
    #    D[c]=row
    #resp = jsonify(D)
    #return resp, 200


@app.errorhandler(404)
def not_found(error=None):
    message = { 'status': 404, 'message': 'Not Found: ' + request.url }
    #resp = jsonify(message)
    #resp.status_code=404
    #return resp
    return jsonify(message), 404

#@app.errorhandler(500)
#def internal_server_error(error=None):
#    message = { 'status': 500, 'message': 'Internal Server Error: ' + request.error }

#@app.errorhandler(Exception)
#def all_exception_handler(e):
#    error = str(traceback.format_exc())
#    return jsonify(error), 500

#@app.errorhandler(500)
@app.errorhandler(Exception)
def handle_exception(e):
    if isinstance(e, HTTPException):
        return e
    res = {'status': 500, 'errorType': 'Internal Server Error'}
    #print(str(e))
    #res['errorMessage'] = e.message if hasattr(e, 'message') else f'{e}'
    res['errorMessage'] = str(e)
    return jsonify(res), 500


if __name__ == "__main__":
    app.run(port=8980, debug=False)


