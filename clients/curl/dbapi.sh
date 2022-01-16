#!/bin/bash

sql(){
curl --user dbuser:dbpass \
     -X POST \
     -H "Content-Type: text/sql" \
     --data "$1" \
     "http://127.0.0.1:8980/api"
}

usage(){
  echo "Usage: $0 sql 'sql statement'"
}

case $1 in
  sql) sql "$2";;
  *)usage;;
esac

