
# -*- coding: utf-8 -*-

"""setup.py: setuptools control."""

from setuptools import setup

setup(
    name = "db-api-server",
    packages = ["db_api_server"],
    entry_points = {
        "console_scripts": ['db-api-server = db_api_server.server:main']
        },
    version = '1.0.5',
    description = "db-api-server flask mysql.connector",
    long_description = "RESTful API for mysql/mariadb",
    author = "Karl Rink",
    author_email = "karl@rink.us",
    url = "https://gitlab.com/krink/db-api-server",
    install_requires = [ 'flask', 'flask-cors', 'mysql.connector' ]
    )


