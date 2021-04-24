
from app import app
from flaskext.mysql import MySQL

mysql = MySQL()

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = ''
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = '' 
app.config['MYSQL_DATABASE_HOST'] = ''
app.config['MYSQL_DATABASE_PORT'] = ''

mysql.init_app(app)

