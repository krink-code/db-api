
# -*- coding: utf-8 -*-

"""wsgi: Web Server Gateway Interface."""

from __future__ import absolute_import
from src.db_api_server.server import app

if __name__ == "__main__":
    app.run()

