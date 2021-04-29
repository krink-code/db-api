
# PATCH

#curl -i --user dbuser:dbpass \
curl --user dbuser:dbpass \
     -X PATCH  \
     -H "Content-Type: application/json" \
     -H "Accept: application/json"  \
     -d '{"description": "A PATCH update2"}' \
    http://127.0.0.1:8980/api/example/table1/9

     #-d '{"name": "Krink","description": "A PATCH update"}' \

     #if description is already "A PATCH update"... 465


#🐰 karl.rink@Karl-MacBook-Pro Notes % ./client3.bash
#{"message":"Created","status":201,"update":"Success"}
#🐰 karl.rink@Karl-MacBook-Pro Notes % ./client3.bash
#{"message":"Failed Update","status":465}
#🐰 karl.rink@Karl-MacBook-Pro Notes %


