import os
import datetime
import random


def get_mnnFile(filePath):
    f_list = os.listdir(filePath)
    mnnFile_list = []
    for i in f_list:
        if os.path.splitext(i)[-1] == ".mnn" and i != "init.mnn" and i != 'mnist.snapshot.mnn':
            mnnFile_list.append(i)
    return mnnFile_list


def get_randomFileName():
    nowTime = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    randomNum = random.randint(0, 100)
    if randomNum <= 10:
        randomNum = str(0) + str(randomNum)
    uniqueNum = str(nowTime) + str(randomNum)
    return uniqueNum

