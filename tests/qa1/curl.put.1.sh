
curl --user dbuser:dbpass \
     --request PUT \
     --header 'Content-Type: application/json' \
     --data '{"id":1, "name":"hello", "description":"replaced via curl"}' \
     http://127.0.0.1:8980/api/example/table1

