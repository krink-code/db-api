
post_form=$(

curl -s -X POST \
     -F "credentials='ZGJ1c2VyOmRicGFzcw=='" \
     -F "name='qa1'" \
     -F "description='form data'" \
     "http://127.0.0.1:8980/api/example/table1"

if [ $? -ne 0 ]
then
    echo $?
    exit $?
fi
)

if echo $post_form | grep -q 201
then #echo 'success'
    echo $post_form
else
    echo $post_form
    echo 'fail'
    exit 1
fi

