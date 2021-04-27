
# python3

__version__='0.0.1.dev.20210427-3'

from app import app
from flask import request
from flask import jsonify
from werkzeug.exceptions import HTTPException
from db import mysql
import cryptography
from functools import wraps


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

    fields = request.args.get("fields", None)
    if not fields:
        fields = '*'
    limit  = request.args.get("limit", None)

    if not request.query_string:
        SQL = 'SHOW FIELDS FROM ' + str(db) +'.'+ str(table)
        rows = fetchall(SQL)
        return jsonify(rows), 200

    SQL = 'SELECT '+ str(fields) +' FROM '+ str(db) +'.'+ str(table) 

    if limit:
        SQL += ' LIMIT ' + str(limit)

    rows = fetchall(SQL)
    return jsonify(rows), 200


#GET    /api/<db>/<table>/:id         # Retrieve a row by primary key
@app.route("/api/<db>/<table>/<key>", methods=['GET'])
def get_one(db=None, table=None, key=None):

    assert db == request.view_args['db']
    assert table == request.view_args['table']
    assert key == request.view_args['key']

    fields = request.args.get("fields", None)
    if not fields:
        fields = '*'

    SQL = "SELECT "+ str(fields) +" FROM "+ str(db) +"."+ str(table) +" WHERE id='"+str(key)+"'"
    row = fetchone(SQL)
    return jsonify(row), 200

#POST   /api/<db>/<table>             # Create a new row
@app.route("/api/<db>/<table>", methods=['POST'])
def post_insert(db=None, table=None):

    assert db == request.view_args['db']
    assert table == request.view_args['table']

    #... 

    #return jsonify({'status': 201, 'message':'Created'}), 201
    return jsonify(status=201, message="Created"), 201





@app.errorhandler(404)
def not_found(error=None):
    message = { 'status': 404, 'errorType': 'Not Found: ' + request.url }
    return jsonify(message), 404


@app.errorhandler(Exception)
def handle_exception(e):
    if isinstance(e, HTTPException):
        return e
    res = {'status': 500, 'errorType': 'Internal Server Error'}
    res['errorMessage'] = str(e)
    return jsonify(res), 500


def Auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        app.config['MYSQL_DATABASE_USER'] = request.authorization.username
        app.config['MYSQL_DATABASE_PASSWORD'] = request.authorization.password
        app.config['MYSQL_DATABASE_HOST'] = request.headers.get('X-Host', '127.0.0.1')
        app.config['MYSQL_DATABASE_PORT'] = int(request.headers.get('X-Port', '3306'))
        return f(*args, **kwargs)
    return decorated


@Auth
def fetchall(sql):
    conn = mysql.connect()
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

@Auth
def fetchone(sql):
    conn = mysql.connect()
    cur = conn.cursor()
    cur.execute(sql)
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row




if __name__ == "__main__":
    app.run(port=8980, debug=False)


