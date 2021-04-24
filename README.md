

http://127.0.0.1:8980/api/<db>/<table>/

---

GET    /                             # Show status

GET    /api/                         # Show databases
GET    /api/<db>                     # Show database tables
GET    /api/<db>/<table>             # Show database table fields

GET    /api/<db>/<table>?query=true  # List rows of table
POST   /api/<db>/<table>             # Create a new row
PUT    /api/<db>/<table>             # Replaces existing row with new row

GET    /api/<db>/<table>/:id         # Retrieve a row by primary key
PATCH  /api/<db>/<table>/:id         # Updates row element by primary key
DELETE /api/<db>/<table>/:id         # Delete a row by primary key

GET    /api/<db>/<table>/count       # Count number of rows in a table

---

Production deployment
https://gunicorn.org/#deployment

---

REST
https://en.wikipedia.org/wiki/Representational_state_transfer


