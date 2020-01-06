#! usr/bin/python3
# -*- coding: utf-8 -*-

from app import create_app
# from flask import request, jsonify, g
# from utils.token_utils import ResolveCacheToken
from flask_babelex import Babel
from flask import request,jsonify

# from flask_sockets import Sockets
# import datetime,time
# from gevent import pywsgi
# from geventwebsocket.handler import WebSocketHandler


app = create_app()
babel = Babel(app)

# sockets = Sockets(app,path='/socket/user1/')
#
# @sockets.route('/socket')
# def socket(ws):
#     while not ws.closed:
#         message = ws.receive()
#         ws.send(str(message))




# @socketio.on("connect")
# def socket():
#     json_data = request.get_json()
#     socketdata = json_data["socketdata"]
#     socketio.emit('wesocket',
#                   {'data': socketdata})
#     return jsonify({
#         "code":1,
#         "data": socketdata
#     })

# def tokenverify():
#     if request.method == "POST":
#         if request.path == "/backstage/login/":
#             pass
#         else:
#             if request.is_json:
#                 token = request.get_json().get("token")
#             else:
#                 token = request.headers.get("token")
#
#             p = ResolveCacheToken().resolve(token)
#             g.token = p
#
#             if not isinstance(p, dict):
#                 return jsonify({
#                     "code": -1,
#                     "data": "请重新登陆"
#                 })
#
#             elif request.method == "OPTIONS":
#                 return jsonify({
#                     "code": 1,
#                     "data": "预检成功"
#                 })
#     else:
#         return jsonify({
#             "code": -1,
#             "data": "数据格式错误"
#         })

if __name__ == "__main__":
    app.run()
    # socketio.run(app)
    # server = pywsgi.WSGIServer(('19.130.223.136', 81), app, handler_class=WebSocketHandler)
    # # print('server start')
    # server.serve_forever()
