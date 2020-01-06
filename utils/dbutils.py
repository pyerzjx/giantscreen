#! usr/bin/python3
# -*- coding: utf-8 -*-
from flask_redis import Redis
from flask_sqlalchemy import SQLAlchemy

redis = Redis()


db = SQLAlchemy()
admin_session = db.session

def makeDictFactory(cursor):
    columnNames = [d[0] for d in cursor.description]

    def createRow(*args):
        return dict(zip(columnNames, args))

    return createRow
