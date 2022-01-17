#!/bin/bash

dbapi(){
curl --user dbuser:dbpass \
     -X POST \
     -H "Content-Type: text/sql" \
     --data "$1" \
     http://127.0.0.1:8980/api
}

usage(){
  echo "Usage: $0 'sql statement'"
}

if [ "$1" ]; then
    dbapi "$1"
else
    usage
fi

