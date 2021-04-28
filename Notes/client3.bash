
# PATCH

#curl -i --user dbuser:dbpass \
curl --user dbuser:dbpass \
     -X PATCH  \
     -H "Content-Type: application/json" \
     -H "Accept: application/json"  \
     -d '{"description": "A PATCH update"}' \
    http://127.0.0.1:8980/api/example/table1/3


     #-d '{"name": "Krink","description": "A PATCH update"}' \
