# End2end-Federated-Learning

## 介绍
联邦学习虽然受到了大量关注，但已有工作基本上基于仿真测试，没有一个完整的系统供大家研究。为此我们搭了一个端到端的跨终端联邦学习系统，并在20台真实安卓设备上做了个验证（demo如下），代码将积极维护和优化，希望可以对社区有所帮助。

## demo演示
![动画](https://user-images.githubusercontent.com/38753457/119235241-07fbd380-bb64-11eb-9d3d-ac47ecc9184d.gif)


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

1.数据和初始化模型通过命令行工具adb下载到Android设备本地

```
cd End2end-Federated-Learning/data
adb push mnist.snapshot.mnn /data/local/tmp/mnn/mnist.snapshot.mnn
adb push mnist_data /data/local/tmp/mnist_data
```

2.修改app/src/main/java/com/demo/MainActivity.java中的SERVER_URL为服务端的ip地址

3.连接android设备，并运行项目（必须和服务端在同一个局域网下才能正常运行）


## 联系我们

[徐梦玮教授](https://xumengwei.github.io/), [王尚广教授](http://www.sguangwang.com/)
