
# PUT replace record

curl --user dbuser:dbpass \
    --request PUT \
    --header 'Content-Type: application/json' \
    --data '{"id":7, "name":"hello", "description":"replaced via curl"}' \
    http://127.0.0.1:8980/api/example/table1  


    #--data '{"id":"NULL","name":"hello","description":"inserted via curl","created_at":"NULL"}' \
