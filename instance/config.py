#! usr/bin/python3
# -*- coding: utf-8 -*-

import os

SECRET_KEY = os.urandom(24)
TIMEZONE = 'Asia/Shanghai'

MY_HOST = "19.130.223.53"
MY_PORT = 3306
MY_USER = "root"
DB_PASS = '123456'
DB_ADMIN = 'bgdata'

# 国际化
BABEL_DEFAULT_LOCALE = "zh_CN"

SQLALCHEMY_DATABASE_URI = "mysql+pymysql://{ROOT}:{PASS}@{HOST}:{PORT}/{TABLE}".format(ROOT=MY_USER, PASS=DB_PASS,
                                                                                       HOST=MY_HOST, PORT=MY_PORT,
                                                                                       TABLE=DB_ADMIN)
SQLALCHEMY_ECHO = True
SQLALCHEMY_POOL_SIZE = 100
SQLALCHEMY_POOL_RECYCLE = 25200
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_MAX_OVERFLOW = 20

# Redis数据库

REDIS_HOST = "127.0.0.1"
REDIS_PORT = 6379
#REDIS_PASSWORD = 'DPXT@123456'
REDIS_DB = 4
REDIS_DECODE_RESPONSES = 1
REDIS_ENCODING = 'utf-8'
REDIS_ENCODING_ERRORS = 'ignore'
REDIS_SOCKET_CONNECT_TIME = 1

# api缓存键值
WEBPICACHEKEY = 'webapicache'


# oracle存储过程 数据库
OR_HOST = '19.130.223.59:1521/orcl'
OR_USER = 'dp_readuser'
OR_PW = 'fs12345dp_read'
