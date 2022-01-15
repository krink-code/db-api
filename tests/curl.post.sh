

json(){
curl --user dbuser:dbpass \
     -X POST \
     -H "Content-Type: application/json" \
     --data '{"name":"hello","description":"inserted via post"}' \
     "http://127.0.0.1:8980/api"
}

form(){
curl --user dbuser:dbpass \
     -X POST \
     -H "Content-Type: application/x-www-form-urlencoded" \
     --data "param1=value1&param2=value2" \
     "http://127.0.0.1:8980/api"
}

image(){
curl --user dbuser:dbpass \
     -X POST \
     -H "Content-Type: image/jpg" \
     --data-binary "mluYXJ5Cg==" \
     "http://127.0.0.1:8980/api"
}

binary(){
curl --user dbuser:dbpass \
     -X POST \
     -H "Content-Type: application/octet-stream" \
     --data-binary "mluYXJ5Cg==" \
     "http://127.0.0.1:8980/api"
}

text(){
curl --user dbuser:dbpass \
     -X POST \
     -H "Content-Type: text/plain" \
     --data "select * from db.table where id = '/this/id'" \
     "http://127.0.0.1:8980/api"
}

TEXT(){
curl --user dbuser:dbpass \
     -X POST \
     -H "Content-Type: TEXT/PLAIN" \
     --data "select * from db.table where id = '/this/id'" \
     "http://127.0.0.1:8980/api"
}

textutf8(){
curl --user dbuser:dbpass \
     -X POST \
     -H "Content-Type: text/plain; charset=utf-8" \
     --data "select * from db.table where id = '/this/id'" \
     "http://127.0.0.1:8980/api"
}

test1(){
curl --user dbuser:dbpass \
     -X POST \
     -H "Content-Type: text/plain" \
     --data "select * from example.table1 where name = 'hello'" \
     "http://127.0.0.1:8980/api"
}

test2(){
curl --user dbuser:dbpass \
     -X POST \
     -H "Content-Type: text/plain" \
     --data "select * from example.table1 where name = '/this/id'" \
     "http://127.0.0.1:8980/api"
}

sql(){
#echo "this is $1"
curl --user dbuser:dbpass \
     -X POST \
     -H "Content-Type: text/sql" \
     --data "$1" \
     "http://127.0.0.1:8980/api"
}


usage(){
  echo "Usage: $0 json|form|files|image|binary|text|TEXT|textutf8|sql"
}

case $1 in
  json) json;;
  form) form;;
  files) files;;
  image) image;;
  binary) binary;;
  text) text;;
  TEXT) TEXT;;
  textutf8) textutf8;;
  test1) test1;;
  test2) test2;;
  sql) sql "$2";;
  *)usage;;
esac



