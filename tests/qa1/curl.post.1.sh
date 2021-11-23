

post_json=$(

curl --silent --user dbuser:dbpass \
     -X POST \
     -H "Content-Type: application/json" \
     --data '{"name":"hello","description":"inserted via curl"}' \
     "http://127.0.0.1:8980/api/example/table1"

if [ $? -ne 0 ]
then
    echo $?
    exit $?
fi
)

if echo $post_json | grep -q 201
then #echo 'success'
    echo $post_json
else
    echo $post_json
    echo 'fail'
    exit 1
fi

