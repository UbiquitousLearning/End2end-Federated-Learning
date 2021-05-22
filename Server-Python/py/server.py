#!/usr/bin/python3
# -*- coding: utf-8 -*-
import argparse
import random
import os
import time
import cherrypy
import json
import base64
import MNNAgg
import utils
import threading
import inspect
import ctypes

from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool
from ws4py.websocket import WebSocket
from ws4py.messaging import TextMessage

"""
运行python3 websocket_test.py
在浏览器打开http://localhost:8080/
可以打开server Web
"""

# client and message model
CLIENT = set()
CLIENT_MSG = {}
MODEL_DATA = {}
# the max number of model before training and the number of global epoch
THRESHOLD = 5
EPOCH_LIMIT = 15
# the number of epochs which have been over
EPOCH = 0
# timestamp which is used to calculate time
EPOCH_TIMESTAMP = 0
# timeout setting
TIME_OUT = 30
index = "no"
thread_list = []
BAD_IP = "10.128.223.90"


# Use below two functions to kill the thread
def _async_raise(tid, exctype):
	"""raises the exception, performs cleanup if needed"""
	tid = ctypes.c_long(tid)
	if not inspect.isclass(exctype):
		exctype = type(exctype)
	res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
	if res == 0:
		raise ValueError("invalid thread id")
	elif res != 1:
		# """if it returns a number greater than one, you're in trouble,
		# and you should call it again with exc=NULL to revert the effect"""
		ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
		raise SystemError("PyThreadState_SetAsyncExc failed")


def stop_thread(thread):
	_async_raise(thread.ident, SystemExit)


# choose n clients randomly from ready clients
def choose_client(n):
	return random.sample([client for client in CLIENT if client.peer_address[0] != BAD_IP and (CLIENT_MSG[client.peer_address[0]]["status"] == "ready" or CLIENT_MSG[client.peer_address[0]]["status"] == "waiting")], n)


# aggregate the model and calculate the index such as loss and accuracy
def model_index():
	while True:
		global EPOCH
		global EPOCH_TIMESTAMP
		global index
		global thread_list
		if EPOCH < EPOCH_LIMIT and EPOCH_TIMESTAMP != 0:
			# when the number of models equals to the threshold or (timeout and the numbers of model no less than half of the threshold)
			# then begin to aggreagte the models
			if (time.time() - EPOCH_TIMESTAMP < TIME_OUT and len(MODEL_DATA) == THRESHOLD) \
					or (time.time() - EPOCH_TIMESTAMP >= TIME_OUT and len(MODEL_DATA) >= THRESHOLD / 2):
				for thread in thread_list:
					if thread.isAlive():
						CLIENT_MSG[thread.client.peer_address[0]]["status"] = "ready"
						CLIENT_MSG[thread.client.peer_address[0]]["time"] = "0"
						stop_thread(thread)
				thread_list.clear()

				loss_sum = 0
				train_weight_sum = 0
				acc_sum = 0
				test_weight_sum = 0

				for ip in MODEL_DATA:
					loss_sum = loss_sum + MODEL_DATA[ip]["train_weight"] * MODEL_DATA[ip]["loss"]
					train_weight_sum += MODEL_DATA[ip]["train_weight"]
					acc_sum = acc_sum + MODEL_DATA[ip]["test_weight"] * MODEL_DATA[ip]["acc"]
					test_weight_sum += MODEL_DATA[ip]["test_weight"]
				loss = loss_sum / train_weight_sum
				acc = acc_sum / test_weight_sum

				choose_list = []
				if EPOCH < EPOCH_LIMIT - 1:
					if os.path.exists("../model/mnist.snapshot.mnn"):
						os.remove("../model/mnist.snapshot.mnn")
					MNNAgg.agg_mnnFile(utils.get_mnnFile("../model/"), "../model/mnist.snapshot.mnn", MODEL_DATA)

					f = open("../model/mnist.snapshot.mnn", "rb")
					data = f.read()
					f.close()

					trainingMsg = {}
					trainingMsg["kind"] = "aggregate"
					trainingMsg["localEpochs"] = "5"
					trainingMsg["batchSize"] = "64"
					trainingMsg["learningRate"] = "0.01"
					trainingMsg["model"] = base64.b64encode(data).decode("utf-8")
					trainingMsg["downloadTimestamp"] = str(int(time.time() * 1000))
					trainingMsg = json.dumps(trainingMsg).encode()

					choose_list = choose_client(THRESHOLD)
					for client in choose_list:
						# client.send(trainingMsg)
						t = send_json(client, trainingMsg)
						t.setDaemon(True)
						thread_list.append(t)
					for t in thread_list:
						t.start()
						t.join()

				mnn_file = utils.get_mnnFile("../model/")
				for file in mnn_file:
					os.remove("../model/" + file)
				for ip in CLIENT_MSG:
					if CLIENT_MSG[ip]["status"] != "connect":
						CLIENT_MSG[ip]["status"] = "ready"
						CLIENT_MSG[ip]["time"] = "0"
				for client in choose_list:
					CLIENT_MSG[client.peer_address[0]]["status"] = "running"

				MODEL_DATA.clear()

				EPOCH += 1
				EPOCH_TIMESTAMP = time.time()

				index = str(loss) + " " + str(acc)
			# when timeout and the numbers of model less than half of the threshold
			# then restart the epoch
			elif time.time() - EPOCH_TIMESTAMP >= TIME_OUT and len(MODEL_DATA) < THRESHOLD / 2:
				for thread in thread_list:
					if thread.isAlive():
						CLIENT_MSG[thread.client.peer_address[0]]["status"] = "ready"
						CLIENT_MSG[thread.client.peer_address[0]]["time"] = "0"
						stop_thread(thread)
				thread_list.clear()

				model_dir = ("../model/init.mnn" if (EPOCH == 0) else "../model/mnist.snapshot.mnn")
				f = open(model_dir, "rb")
				data = f.read()
				f.close()

				trainingMsg = {}
				trainingMsg["kind"] = "aggregate"
				trainingMsg["localEpochs"] = "5"
				trainingMsg["batchSize"] = "64"
				trainingMsg["learningRate"] = "0.01"

				trainingMsg["model"] = base64.b64encode(data).decode("utf-8")
				trainingMsg["downloadTimestamp"] = str(int(time.time() * 1000))
				trainingMsg = json.dumps(trainingMsg).encode()

				choose_list = choose_client(THRESHOLD)
				thread_list = []
				for client in choose_list:
					t = send_json(client, trainingMsg)
					t.setDaemon(True)
					thread_list.append(t)
				for t in thread_list:
					t.start()
					t.join()

				mnn_file = utils.get_mnnFile("../model/")
				for file in mnn_file:
					os.remove("../model/" + file)
				for ip in CLIENT_MSG:
					if CLIENT_MSG[ip]["status"] != "connect":
						CLIENT_MSG[ip]["status"] = "ready"
						CLIENT_MSG[ip]["time"] = "0"
				for client in choose_list:
					CLIENT_MSG[client.peer_address[0]]["status"] = "running"

				index = "no"
			else:
				index = "no"
		else:
			index = "no"
		time.sleep(1)


# send_json function, which used to establish the thread to send message
class send_json(threading.Thread):
	def __init__(self, client, msg):
		super(send_json, self).__init__()
		self.client = client
		self.msg = msg

	def run(self):
		self.client.send(self.msg)


# websocket
class ChatWebSocketHandler(WebSocket):

	# receive connection request
	def opened(self):
		timeArray = time.localtime(int(time.time()))
		CLIENT.add(self)
		CLIENT_MSG[self.peer_address[0]] = {}
		CLIENT_MSG[self.peer_address[0]]["status"] = "connect"
		CLIENT_MSG[self.peer_address[0]]["time"] = "0"
		print("[",time.strftime("%Y-%m-%d %H:%M:%S", timeArray),"]","receive connect from ",self.peer_address)
		print("[",time.strftime("%Y-%m-%d %H:%M:%S", timeArray),"]","current client num:",len(CLIENT_MSG))

	# receive send_data request
	def received_message(self, m):
		# receive String
		if m.is_text:
			recvStr = m.data.decode("utf-8")
			if "hello" == recvStr:
				CLIENT_MSG[self.peer_address[0]]["status"] = "ready"
				timeArray = time.localtime(int(time.time()))
				print("[",time.strftime("%Y-%m-%d %H:%M:%S", timeArray),"]",self.peer_address[0]," joined the system")
				print("[",time.strftime("%Y-%m-%d %H:%M:%S", timeArray),"]",len([ip for ip in CLIENT_MSG if CLIENT_MSG[ip]["status"] == "ready"])," client joined the system")
				print("[",time.strftime("%Y-%m-%d %H:%M:%S", timeArray),"]","current client num:",len(CLIENT_MSG))
		# receive ByteString
		if m.is_binary:
			timeArray = time.localtime(int(time.time()))
			print("[", time.strftime("%Y-%m-%d %H:%M:%S", timeArray), "]", "receive mnn model from ",self.peer_address[0])

			recvStr = m.data
			dic = json.loads(recvStr)
			CLIENT_MSG[self.peer_address[0]]["status"] = "waiting"
			now_time = int(round(time.time() * 1000))
			CLIENT_MSG[self.peer_address[0]]["time"] = str((now_time - dic["upload_timestamp"] / 1000))
			self.save_file(base64.b64decode(dic["model"].encode("utf-8")))
			MODEL_DATA[self.peer_address[0]] = {}
			MODEL_DATA[self.peer_address[0]]["train_weight"] = dic["train_samples"]
			MODEL_DATA[self.peer_address[0]]["loss"] = dic["loss"]
			MODEL_DATA[self.peer_address[0]]["test_weight"] = dic["test_samples"]
			MODEL_DATA[self.peer_address[0]]["acc"] = dic["acc"]

	# receive disconnection request
	def closed(self, code, reason="A client left the room without a proper explanation."):

		timeArray = time.localtime(int(time.time()))
		print("[", time.strftime("%Y-%m-%d %H:%M:%S", timeArray), "]", self.peer_address[0], "connect closed")
		CLIENT.remove(self)
		del CLIENT_MSG[self.peer_address[0]]
		print("[", time.strftime("%Y-%m-%d %H:%M:%S", timeArray), "]","current client num:", len(CLIENT_MSG))

		cherrypy.engine.publish("websocket-broadcast", TextMessage(reason))

	# save the data of model to specify folder
	def save_file(self,data, url="../model/"):
		file_name = self.peer_address[0] + "mnist.snapshot.mnn"
		if url == "none":
			path = file_name
		else:
			path = url + file_name
		f = open(path, "wb")
		f.write(data)
		f.close()


# Root
class Root(object):
	def __init__(self, host, port, ssl=False):
		self.host = host
		self.port = port
		self.scheme = "wss" if ssl else "ws"

	# connect clients' number
	@cherrypy.expose()
	def get_client_num(self):
		return "connected clients number:" + str(len(CLIENT_MSG))

	# ready clients' number
	@cherrypy.expose()
	def get_ready_num(self):
		return "ready clients number:" + str(len([ip for ip in CLIENT_MSG if CLIENT_MSG[ip]["status"] == "ready"]))

	# global epoch
	@cherrypy.expose()
	def get_global_epoch_num(self):
		return "global epoch number:" + str(EPOCH)

	# global epoch timestamp which is used to calculate time of each global epoch
	@cherrypy.expose()
	def get_global_epoch_timestamp(self):
		return str(EPOCH_TIMESTAMP)

	# the message of all clients
	@cherrypy.expose()
	def get_client_msg(self):
		return json.dumps(CLIENT_MSG)

	# the index such as loss and accuracy
	@cherrypy.expose()
	def get_model_index(self):
		return index

	# send the request to start learning
	@cherrypy.expose()
	def send_task(self):
		global EPOCH
		global EPOCH_TIMESTAMP
		mnn_file = utils.get_mnnFile("../model/")
		for file in mnn_file:
			os.remove("../model/" + file)
		if os.path.exists("../model/mnist.snapshot.mnn"):
			os.remove("../model/mnist.snapshot.mnn")

		timeArray = time.localtime(int(time.time()))
		print("[",time.strftime("%Y-%m-%d %H:%M:%S", timeArray),"]","send task back to client")
		# the config of learning
		trainingMsg = {}
		trainingMsg["kind"] = "send_task"
		trainingMsg["localEpochs"] = "5"
		trainingMsg["batchSize"] = "64"
		trainingMsg["learningRate"] = "0.01"

		f = open("../model/init.mnn", "rb")
		data = f.read()
		f.close()
		trainingMsg["model"] = base64.b64encode(data).decode("utf-8")
		trainingMsg["downloadTimestamp"] = str(int(time.time() * 1000))
		trainingMsg = json.dumps(trainingMsg).encode()

		EPOCH = 0
		EPOCH_TIMESTAMP = time.time()

		choose_list = choose_client(THRESHOLD)
		thread_list = []
		for client in choose_list:
			t = send_json(client, trainingMsg)
			t.setDaemon(True)
			thread_list.append(t)
		for t in thread_list:
			t.start()
			t.join()

		for client in choose_list:
			CLIENT_MSG[client.peer_address[0]]["status"] = "running"

		return str(EPOCH_TIMESTAMP)

	@cherrypy.expose
	def index(self):
		return open(u"../test.html")

	@cherrypy.expose
	def ws(self):
		# you can access the class instance through
		handler = cherrypy.request.ws_handler


if __name__ == "__main__":

	mnn_file = utils.get_mnnFile("../model/")
	for file in mnn_file:
		os.remove("../model/" + file)
	if os.path.exists("../model/mnist.snapshot.mnn"):
		os.remove("../model/mnist.snapshot.mnn")

	t = threading.Thread(target=model_index, name="modelIndexThread")
	t.start()

	parser = argparse.ArgumentParser(description="Echo CherryPy Server")
	parser.add_argument("--host", default="0.0.0.0")
	parser.add_argument("-p", "--port", default=8080, type=int)
	parser.add_argument("--ssl", action="store_true")
	args = parser.parse_args()

	cherrypy.config.update({"server.socket_host": args.host,
							"server.socket_port": args.port,
							"tools.staticdir.root": os.path.abspath(os.path.join(os.path.dirname(__file__), "static"))})

	if args.ssl:
		cherrypy.config.update({"server.ssl_certificate": "./server.crt",
								"server.ssl_private_key": "./server.key"})
							
	WebSocketPlugin(cherrypy.engine).subscribe()
	cherrypy.tools.websocket = WebSocketTool()
	cherrypy.quickstart(Root(args.host, args.port, args.ssl), "", config={
		"/ws": {
			"tools.websocket.on": True,
			"tools.websocket.handler_cls": ChatWebSocketHandler
			}
		}
	)
