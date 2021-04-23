
# python3

__version__='0.0.0-1'

from flask import Flask
from flask import request
from flask import jsonify

app = Flask(__name__)

@app.route("/", methods=['GET'])
def root():
    return jsonify(status=200, message="OK", version=__version__), 200

@app.errorhandler(404)
def not_found(error=None):
    message = { 'status': 404, 'message': 'Not Found: ' + request.url }
    #resp = jsonify(message)
    #resp.status_code=404
    #return resp
    return jsonify(message), 404

if __name__ == "__main__":
    app.run(port=8980, debug=False)


