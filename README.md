# End2end-Federated-Learning
A demo of end-to-end federated learning system.

[中文版本](https://github.com/UbiquitousLearning/End2end-Federated-Learning/blob/main/README_CN.md)

## Introduce

Federated learning gets a lot of attention recently, but the existing work is basically based on simulation testing, and there is no complete system for everyone to study. Therefore, we built an end-to-end cross-terminal federated learning system and tested it on 20 real Android devices（demo below）. The code will be actively maintained and optimized, and hope it is useful for open source comunity.

## Demo

![动画](https://user-images.githubusercontent.com/38753457/119244767-65187900-bba6-11eb-8bc6-8b9bf0d7f4d8.gif)

## Run Guide

### Server

1. Install python3.6, pip3, and install the following dependency packages

```
pip3 install -U MNN
pip3 install cherrypy
pip3 install ws4py
```

2. Run server.py

### Client
1. The data and initialization model need to be downloaded to the local Android device through the command line tool adb

```
cd End2end-Federated-Learning/data
adb push mnist.snapshot.mnn /data/local/tmp/mnn/mnist.snapshot.mnn
adb push mnist_data /data/local/tmp/mnist_data
```

2. Modify the SERVER_URL in app/src/main/java/com/demo/MainActivity.java to the ip address of the your server
 
3. Connect the android device and run the project (must be in the same local area network as the server to run normally)


## Related Work

[MNN](https://github.com/alibaba/MNN)

## Contact us: [Prof. Mengwei Xu](https://xumengwei.github.io/), [Prof. Shangguang Wang](http://www.sguangwang.com/)
