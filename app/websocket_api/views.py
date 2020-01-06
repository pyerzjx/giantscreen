from flask import Flask, Blueprint
import json

ws = Blueprint(r'socket', __name__)


@ws.route('/<client_name>')
def echo_socket(socket,client_name):

	while not socket.closed:
		message = socket.receive()
		# socket.send(json.dumps({"client_name": client_name}))
		client_name= client_name
		socket.send(json.dumps(message))
