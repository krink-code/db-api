# RESTful API for mysql/mariadb   

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
PUT    /api/<db>/<table>             # Replaces existing row with new row

GET    /api/<db>/<table>/:id         # Retrieve a row by primary key
PATCH  /api/<db>/<table>/:id         # Update row element by primary key
DELETE /api/<db>/<table>/:id         # Delete a row by primary key

GET    /api/<db>/<table>/count       # Count number of rows in a table
```   

---
### Development HTTP service
```   
python3 main.py
```   

### curl client examples

#### get service
```  
curl 127.0.0.1:8980/
```
#### list all databases
```  
curl --user dbuser:dbpass http://127.0.0.1:8980/api
```
#### list all tables in the mysql database
```  
curl --user dbuser:dbpass http://127.0.0.1:8980/api/mysql
```
#### list all table fields in the user table
```  
curl --user dbuser:dbpass http://127.0.0.1:8980/api/mysql/user
```
#### query the mysql.user table fields=user,host,password and limit 3
```  
curl --user dbuser:dbpass "http://127.0.0.1:8980/api/mysql/user?fields=user,host,password&limit=3"
```
#### query example database on different host and port (default is 127.0.0.1:3306)
```  
curl --user dbuser:dbpass -H "X-Host: 127.0.1.1" -H "X-Port: 3307" "http://127.0.0.1:8980/api/example/table?fields=field1,field2,field3"
```


---    

### Production deployment
https://gunicorn.org/#deployment

---

### RESTful
https://en.wikipedia.org/wiki/Representational_state_transfer



