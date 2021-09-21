
# db-api-server

## RESTful API for mysql/mariadb   

```   
http://127.0.0.1:8980/api/<db>/<table>/  
```  
```   
GET    /                             # Show status

GET    /api                          # Show databases
GET    /api/<db>                     # Show database tables
GET    /api/<db>/<table>             # Show database table fields

GET    /api/<db>/<table>?query=true  # List rows of table
POST   /api/<db>/<table>             # Create a new row
PUT    /api/<db>/<table>             # Replace existing row with new row

GET    /api/<db>/<table>/:id         # Retrieve a row by primary key
PATCH  /api/<db>/<table>/:id         # Update row element by primary key
DELETE /api/<db>/<table>/:id         # Delete a row by primary key

GET    /api/<db>/<table>/count       # Count number of rows in a table
```   

[![Package Version](https://img.shields.io/pypi/v/db-api-server.svg)](https://pypi.python.org/pypi/db-api-server/)
[![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/release/python-360/)
[![Python 3.7](https://img.shields.io/badge/python-3.7-blue.svg)](https://www.python.org/downloads/release/python-370/)
[![Python 3.8](https://img.shields.io/badge/python-3.8-blue.svg)](https://www.python.org/downloads/release/python-380/)
[![Python 3.9](https://img.shields.io/badge/python-3.9-blue.svg)](https://www.python.org/downloads/release/python-390/)
 

---   
 
### Development HTTP service (run from source)    
```   
python3 src/db_api_server/server.py   
```   

---   

### pip install  
```
pip install db-api-server
```

### Run command line
```
$ db-api-server  
 * Serving Flask app "db_api_server.server" (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
 * Running on http://127.0.0.1:8980/ (Press CTRL+C to quit)
```

### Run python module
```
python3 -m db_api_server
```

---   

### python client using request module   
```
import requests
req = requests.get('http://127.0.0.1:8980/api',   
               auth=requests.auth.HTTPBasicAuth('username', 'password'))
print(req.text)
```

---

### javascript client using fetch
```
fetch('http://127.0.0.1:8980/api', {
    method: 'GET',
    headers: { Authorization: 'Basic ' + base64 }
})
    .then(response => response.json())
    .then(json => document.write(json))
    .catch(err => document.write('Request Failed', err));
```

---   

### curl client examples   

#### get service HTTP GET   
```   
curl 127.0.0.1:8980/   
```   
#### list all databases HTTP GET   
```  
curl --user dbuser:dbpass http://127.0.0.1:8980/api   
```   
#### list all tables in the mysql database HTTP GET   
```    
curl --user dbuser:dbpass http://127.0.0.1:8980/api/mysql   
```   
#### list all table fields in the user table HTTP GET   
```  
curl --user dbuser:dbpass http://127.0.0.1:8980/api/mysql/user   
```   
#### query the mysql.user table fields=user,host and limit 2,3 HTTP GET   
```  
curl --user dbuser:dbpass "http://127.0.0.1:8980/api/mysql/user?fields=user,host&limit=2,3"   
```   
#### query example database on different host and port (default is 127.0.0.1:3306) HTTP GET   
```  
curl --user dbuser:dbpass -H "X-Host: 127.0.1.1" -H "X-Port: 3307" "http://127.0.0.1:8980/api/example/table?fields=field1,field2,field3"   
```   
#### get record 3 from example database table1 HTTP GET   
```   
curl --user dbuser:dbpass http://127.0.0.1:8980/api/example/table1/3   
```   
#### get record 3 from example database table1 by name=47245ec8-a7d3-11eb-880f-acde48001122 with fields id,name HTTP GET   
```   
curl --user dbuser:dbpass http://127.0.0.1:8980/api/example/table1/47245ec8-a7d3-11eb-880f-acde48001122?column=name&fields=id,name"   
```   
#### insert a new row into example database table1 HTTP POST   
```   
curl --user dbuser:dbpass \
     -X POST \
     -H "Content-Type: application/json" \   
     --data '{"name":"hello","description":"inserted via curl"}' \   
     "http://127.0.0.1:8980/api/example/table1"   
```  

base64(dbuser:dbpass)

```   
curl -X POST \
     -H "Authorization: Basic <base64>" \
     -H "Content-Type: application/json" \
     --data '{"name":"hello","description":"inserted via post"}' \
     "http://127.0.0.1:8980/api/example/table1"
``` 

form data requires credentials in base64 encoding

```
    <form action="http://127.0.0.1:8980/api/example/table1" method="POST">
      <input type="text" name="credentials" value="base64">
      <input type="text" name="name" value="name">
      <input type="text" name="description" value="form data">
      <input type="submit">
    </form>
```

#### update a row element by primary key id=9 HTTP PATCH   
```   
curl --user dbuser:dbpass \   
     -X PATCH  \   
     -H "Content-Type: application/json" \   
     -H "Accept: application/json"  \   
     -d '{"description": "A single colmn update"}' \   
    http://127.0.0.1:8980/api/example/table1/9    
```   
#### update a row element specify name=47245ec8-a7d3-11eb-880f-acde48001122 HTTP PATCH   
```   
curl --user dbuser:dbpass \   
     -X PATCH  \   
     -H "Content-Type: application/json" \   
     -H "Accept: application/json"  \   
     -d '{"description": "A single colmn update2"}' \   
    "http://127.0.0.1:8980/api/example/table1/47245ec8-a7d3-11eb-880f-acde48001122?column=name"   
```

#### delete record id=3 HTTP DELETE   
```   
curl --user dbuser:dbpass \   
     -X DELETE  \   
    http://127.0.0.1:8980/api/example/table1/3   
```   
#### delete a record specify primary key name=47245ec8-a7d3-11eb-880f-acde48001122 HTTP DELETE   
```   
curl --user dbuser:dbpass \   
     -X DELETE  \   
    "http://127.0.0.1:8980/api/example/table1/47245ec8-a7d3-11eb-880f-acde48001122?column=name"   
```   
#### replace records into example database table1  HTTP PUT   
```   
curl --user dbuser:dbpass \   
    --request PUT \   
    --header 'Content-Type: application/json' \   
    --data '{"id":7, "name":"hello", "description":"replaced via curl"}' \   
    http://127.0.0.1:8980/api/example/table1     
```   

---    

```
db-api-server
``` 
https://pypi.org/project/db-api-server    


### docker    
```
docker pull dcsops/db-api
```
https://hub.docker.com/r/dcsops/db-api


### Production deployments   
https://gunicorn.org/#deployment   

---   

### RESTful   
https://en.wikipedia.org/wiki/Representational_state_transfer   

### Basic auth   
https://en.wikipedia.org/wiki/Basic_access_authentication

### Base64   
https://en.wikipedia.org/wiki/Base64    


