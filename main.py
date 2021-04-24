
# python3

__version__='0.0.0-1a'

from app import app
from flask import request
from flask import jsonify
from werkzeug.exceptions import HTTPException

from db import mysql

@app.route("/", methods=['GET'])
def root():
    return jsonify(status=200, message="OK", version=__version__), 200

@app.route("/mysql/user", methods=['GET'])
def mysql_user():

    #/api/payments?_fields=customerNumber,checkNumber

    #curl 'localhost:8980/mysql/user?skip=0&limit=2'
    #curl 'localhost:8980/mysql/user?fields=user,host,plugin'

    limit  = request.args.get("limit", None)
    skip   = request.args.get("skip", None)
    fields = request.args.get("fields", None)
    #if limit:
    #    print(limit)

    conn = mysql.connect()
    #cur = conn.cursor(buffered=True)
    cur = conn.cursor()
    #cur.execute("SELECT * FROM mysql.user;")
    #(('localhost', 'mariadb.sys', '', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', '', '', '', '', 0, 0, 0, 0, 'mysql_native_password', '', 'N', 'N', '', Decimal('0.000000'))
    #{"errorMessage":"Object of type Decimal is not JSON serializable","errorType":"Internal Server Error","status":500}
    cur.execute("SELECT host,user,plugin FROM mysql.user;")
    rows = cur.fetchall()
    #print(str(rows))
    D={}
    c=0
    for row in rows:
        c+=1
        D[c]=row

    resp = jsonify(D)
    cur.close()
    conn.close()
    return resp, 200


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


