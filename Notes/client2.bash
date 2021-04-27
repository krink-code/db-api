

curl --user dbuser:dbpass --request POST --header 'Content-Type: application/json' \
    --data '{"name":"hello","description":"inserted via curl"}' \
    http://127.0.0.1:8980/api/example/table1  


    #--data '{"id":"NULL","name":"hello","description":"inserted via curl","created_at":"NULL"}' \
