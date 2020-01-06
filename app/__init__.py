#! usr/bin/python3
# -*- coding: utf-8 -*-
"""
初始化flask
"""

from flask import Flask
from flask_cors import CORS
from utils.dbutils import redis
from utils.admin_util import admin
from utils.dbutils import db
from utils.websocket_util import Sockets


def create_app():
    """创建app"""
    app = Flask(__name__, instance_relative_config=True, template_folder='../templates')
    CORS(app, supports_credentials=1)

    # 加载配置
    app.config.from_object('config.default')
    app.config.from_object('config.development')
    app.config.from_pyfile('config.py')
    app.config['JSON_AS_ASCII'] = False
    redis.init_app(app)
    admin.init_app(app)
    db.init_app(app)

    # 注册 socketio app
    sockets = Sockets(app)

    # 错误蓝图注册
    from app.error_handler.views import error_handler
    app.register_blueprint(error_handler, url_prefix="/error_handler")

    # api蓝图注册
    from app.webapi.views import webapi
    app.register_blueprint(webapi, url_prefix="/webapi")

    # socket蓝图注册
    from app.websocket_api.views import ws
    sockets.register_blueprint(ws, url_prefix="/socket")
    return app
