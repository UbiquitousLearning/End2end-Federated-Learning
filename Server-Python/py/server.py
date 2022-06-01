#!/usr/bin/python3
# -*- coding: utf-8 -*-
import argparse
import base64
import clientThread
import cherrypy
import json
import numpy
import os
import random
import threading
import time
import utils

from parameter import *
from ws4py.messaging import TextMessage
from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool
from ws4py.websocket import WebSocket


def choose_client(n):
    return random.sample([client for client in para.client
                          if para.client_msg[client.peer_address[0]]["status"] == "ready" or para.client_msg[client.peer_address[0]]["status"] == "waiting"], n)


def model_index():
    while True:
        if para.epoch < para.epoch_limit and para.timestamp != 0:
            old_timestamp = para.timestamp
            if ((time.time() - old_timestamp < para.time_out and len(para.model_data) == para.threshold)
        or (time.time() - old_timestamp >= para.time_out and len(para.model_data) >= para.threshold / 2)):
                for thread in para.thread_list:
                    if thread.isAlive():
                        para.client_msg[thread.client.peer_address[0]]["status"] = "ready"
                        para.client_msg[thread.client.peer_address[0]]["time"] = "0"
                        clientThread.stop_thread(thread)
                para.thread_list.clear()

                loss_sum = 0
                train_weight_sum = 0
                acc_sum = 0
                test_weight_sum = 0

                for ip in para.model_data:
                    loss_sum = loss_sum + para.model_data[ip]["train_weight"] * para.model_data[ip]["loss"]
                    train_weight_sum += para.model_data[ip]["train_weight"]
                    acc_sum = acc_sum + para.model_data[ip]["test_weight"] * para.model_data[ip]["acc"]
                    test_weight_sum += para.model_data[ip]["test_weight"]
                loss = loss_sum / train_weight_sum
                acc = acc_sum / test_weight_sum

                choose_list = []
                para.timestamp = time.time()
                if para.epoch < para.epoch_limit - 1:
                    if os.path.exists("../model/mnist.snapshot.mnn"):
                        os.remove("../model/mnist.snapshot.mnn")
                    os.system("./aggregateModel.out ../model/ ../model/mnist.snapshot.mnn")

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

                    para.timestamp = time.time()

                    choose_list = choose_client(para.threshold)
                    for client in choose_list:
                        t = clientThread.send_json(client, trainingMsg)
                        t.setDaemon(True)
                        para.thread_list.append(t)
                    for t in para.thread_list:
                        t.start()
                        t.join()

                epoch_time = para.timestamp - old_timestamp
                mnn_file = utils.get_mnnFile("../model/")
                for file in mnn_file:
                    os.remove("../model/" + file)
                for ip in para.client_msg:
                    if para.client_msg[ip]["status"] != "connect":
                        para.client_msg[ip]["status"] = "ready"
                        para.client_msg[ip]["time"] = 0
                for client in choose_list:
                    para.client_msg[client.peer_address[0]]["status"] = "running"

                para.model_data.clear()

                para.epoch += 1

                para.acc_list.append(acc)
                para.time_list.append(epoch_time)
                if para.epoch == para.epoch_limit:
                    numpy.save("../result/acc.npy", numpy.array(para.acc_list))
                    numpy.save("../result/time.npy", numpy.array(para.time_list))

                para.index = str(para.epoch) + " " + str(loss) + " " + str(acc) + " " + str(epoch_time)

            elif (time.time() - old_timestamp >= para.time_out
                  and len(para.model_data) < para.threshold / 2):
                for thread in para.thread_list:
                    if thread.isAlive():
                        para.client_msg[thread.client.peer_address[0]]["status"] = "ready"
                        para.client_msg[thread.client.peer_address[0]]["time"] = "0"
                        clientThread.stop_thread(thread)
                para.thread_list.clear()
                model_dir = "../model/init.mnn" if (para.epoch == 0) else "../model/mnist.snapshot.mnn"
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

                choose_list = choose_client(para.threshold)
                for client in choose_list:
                    t = clientThread.send_json(client, trainingMsg)
                    t.setDaemon(True)
                    para.thread_list.append(t)
                for t in para.thread_list:
                    t.start()
                    t.join()

                mnn_file = utils.get_mnnFile("../model/")
                for file in mnn_file:
                    os.remove("../model/" + file)
                for ip in para.client_msg:
                    if para.client_msg[ip]["status"] != "connect":
                        para.client_msg[ip]["status"] = "ready"
                        para.client_msg[ip]["time"] = 0
                for client in choose_list:
                    para.client_msg[client.peer_address[0]]["status"] = "running"

                para.index = "no"
            else:
                para.index = "no"
        else:
            para.index = "no"

        time.sleep(1)


class ChatWebSocketHandler(WebSocket):
    def opened(self):
        timeArray = time.localtime(int(time.time()))
        para.client.add(self)
        para.client_msg[self.peer_address[0]] = {}
        para.client_msg[self.peer_address[0]]["status"] = "connect"
        para.client_msg[self.peer_address[0]]["time"] = 0
        print("[", time.strftime("%Y-%m-%d %H:%M:%S", timeArray), "]", "receive connect from ",
              self.peer_address)
        print("[", time.strftime("%Y-%m-%d %H:%M:%S", timeArray), "]", "current client num:",
              len(para.client_msg))

    def received_message(self, m):
        if m.is_text:
            recvStr = m.data.decode("utf-8")
            if recvStr == "hello":
                para.client_msg[self.peer_address[0]]["status"] = "ready"
                timeArray = time.localtime(int(time.time()))
                print("[", time.strftime("%Y-%m-%d %H:%M:%S", timeArray), "]", self.peer_address[0],
                      " joined the system")
                print("[", time.strftime("%Y-%m-%d %H:%M:%S", timeArray), "]",
                      len([ip for ip in para.client_msg if para.client_msg[ip]["status"] == "ready"]),
                      " clients joined the system")
                print("[", time.strftime("%Y-%m-%d %H:%M:%S", timeArray), "]", "current client num:",
                      len(para.client_msg))

        elif m.is_binary:
            timeArray = time.localtime(int(time.time()))
            print("[", time.strftime("%Y-%m-%d %H:%M:%S", timeArray), "]", "receive mnn model from ",
                  self.peer_address[0])

            now_time = int(round(time.time() * 1000))
            recvStr = m.data
            dic = json.loads(recvStr)
            para.client_msg[self.peer_address[0]]["status"] = "waiting"
            para.client_msg[self.peer_address[0]]["time"] = \
                str(abs(now_time - dic["upload_timestamp"]) / 1000)
            self.save_file(dic["train_samples"], base64.b64decode(dic["model"].encode("utf-8")))
            para.model_data[self.peer_address[0]] = {}
            para.model_data[self.peer_address[0]]["train_weight"] = dic["train_samples"]
            para.model_data[self.peer_address[0]]["loss"] = dic["loss"]
            para.model_data[self.peer_address[0]]["test_weight"] = dic["test_samples"]
            para.model_data[self.peer_address[0]]["acc"] = dic["acc"]

    def closed(self, code, reason="A client left the room without a proper explanation."):
        timeArray = time.localtime(int(time.time()))
        print("[", time.strftime("%Y-%m-%d %H:%M:%S", timeArray), "]", self.peer_address[0],
              "connect closed")
        para.client.remove(self)
        del para.client_msg[self.peer_address[0]]
        print("[", time.strftime("%Y-%m-%d %H:%M:%S", timeArray), "]", "current client num:",
              len(para.client_msg))

        cherrypy.engine.publish("websocket-broadcast", TextMessage(reason))

    def save_file(self, weight, data, url="../model/"):
        path = url + str(weight) + "_" + self.peer_address[0] + "mnist.snapshot.mnn"
        f = open(path, "wb")
        f.write(data)
        f.close()


class Root(object):
    def __init__(self, host, port, ssl=False):
        self.host = host
        self.port = port
        self.scheme = "wss" if ssl else "ws"

    @cherrypy.expose()
    def get_client_num(self):
        return "连接客户端数量：" + str(len(para.client_msg))

    @cherrypy.expose()
    def get_ready_num(self):
        return "就绪客户端数量：" + str(len([ip for ip in para.client_msg
                                    if para.client_msg[ip]["status"] == "ready"]))

    @cherrypy.expose()
    def get_client_msg(self):
        return json.dumps(para.client_msg)

    @cherrypy.expose()
    def get_model_index(self):
        return para.index

    @cherrypy.expose()
    def send_task(self):
        para.acc_list.clear()
        para.time_list.clear()
        if os.path.exists("../result/acc.npy"):
            os.remove("../result/acc.npy")
        if os.path.exists("../result/time.npy"):
            os.remove("../result/time.npy")

        timeArray = time.localtime(int(time.time()))
        print("[", time.strftime("%Y-%m-%d %H:%M:%S", timeArray), "]", "send task back to client")

        f = open("../model/init.mnn", "rb")
        data = f.read()
        f.close()
        trainingMsg = {}
        trainingMsg["kind"] = "send_task"
        trainingMsg["localEpochs"] = "5"
        trainingMsg["batchSize"] = "64"
        trainingMsg["learningRate"] = "0.01"
        trainingMsg["model"] = base64.b64encode(data).decode("utf-8")
        trainingMsg["downloadTimestamp"] = str(int(time.time() * 1000))
        trainingMsg = json.dumps(trainingMsg).encode()

        para.timestamp = time.time()

        choose_list = choose_client(para.threshold)
        for client in choose_list:
            t = clientThread.send_json(client, trainingMsg)
            t.setDaemon(True)
            para.thread_list.append(t)
        for t in para.thread_list:
            t.start()
            t.join()
        for client in choose_list:
            para.client_msg[client.peer_address[0]]["status"] = "running"

    @cherrypy.expose
    def index(self):
        return open(u"../test.html")

    @cherrypy.expose
    def ws(self):
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
                            "tools.staticdir.root": os.path.abspath(
                                os.path.join(os.path.dirname(__file__), os.path.pardir, "static"))})

    if args.ssl:
        cherrypy.config.update({"server.ssl_certificate": "./server.crt",
                                "server.ssl_private_key": "./server.key"})

    WebSocketPlugin(cherrypy.engine).subscribe()
    cherrypy.tools.websocket = WebSocketTool()
    # cherrypy.tools.sessions.timeout = 1000000
    cherrypy.quickstart(Root(args.host, args.port, args.ssl), "", config={
        "/ws": {
            "tools.websocket.on": True,
            "tools.websocket.handler_cls": ChatWebSocketHandler
        },
        "/picture": {
            "tools.staticdir.on": True,
            "tools.staticdir.dir": "picture"
        }
    })