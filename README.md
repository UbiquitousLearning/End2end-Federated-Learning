# End2end-Federated-Learning

## 运行

首先保证服务端和客户端在同一个局域网下：

### 服务端

1.安装python3.6、pip3，并运行以下依赖包

```
pip3 install -U MNN
pip3 install cherrypy
pip3 install ws4py
```

2.运行server.py

### 客户端

1.数据和初始化模型通过adb下载到本地

```
cd End2end-Federated-Learning/data
adb push mnist.snapshot.mnn /data/local/tmp/mnn/mnist.snapshot.mnn
adb push mnist_data /data/local/tmp/mnist_data
```

2.修改app/src/main/java/com/demo/MainActivity.java中的SERVER_URL为服务端的ip地址

3.连接android设备，并运行项目（必须和服务端在同一个局域网下才能正常运行）
