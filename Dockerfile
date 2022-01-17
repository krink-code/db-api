
FROM python:3.8

WORKDIR /app

ADD requirements.txt /app

RUN pip install --no-cache-dir -r requirements.txt

RUN pip install gunicorn

ADD wsgi.py /app
ADD src/db_api_server/server.py /app/src/db_api_server/server.py

CMD gunicorn --bind 0.0.0.0:8980 -w 3 --log-level=info wsgi:APP

EXPOSE 8980

## Dockerfile for db-api
#
### build the docker container
# docker build -t db-api:1.0.0 .
#
### run the docker container local
# docker run -p 8980:8980 -it db-api:1.0.0
#
### push the docker container to registry
# docker push registry:5000/db-api:1.0.0
#
### public registry
# https://hub.docker.com/r/dcsops/db-api
#
# docker push dcsops/db-api:tagname

