
curl --user dbuser:dbpass \
     -X PATCH  \
     -H "Content-Type: application/json" \
     -H "Accept: application/json"  \
     -d '{"description": "A single colmn update2"}' \
    "http://127.0.0.1:8980/api/example/table1/1?column=id"

