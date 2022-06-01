import os


def get_mnnFile(filePath):
    f_list = os.listdir(filePath)
    for f in f_list[:]:
        if os.path.splitext(f)[-1] != ".mnn" or f == "init.mnn" or f == "mnist.snapshot.mnn":
            f_list.remove(f)
    return f_list