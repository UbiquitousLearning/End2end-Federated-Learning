import MNN
import numpy as np
import utils

F = MNN.expr


def agg_mnnFile(mnnFile_list, savePath, MODEL_DATA):
    # weights = mnnFile_list.values()
    elements = [F.load_as_list("../model/" + mnnFile) for mnnFile in mnnFile_list]
    # elements_data = []
    # for element in elements:
    #     data = [var.read() for var in element]
    #     elements_data.append(data)
    # result = []
    MODEL_WEIGHT = [MODEL_DATA[mnnFile[:-len("mnist.snapshot.mnn")]]["train_weight"] for mnnFile in mnnFile_list]
    for i in range(len(elements[0])):
        elements[0][i] *= MODEL_WEIGHT[0]
        for j in range(1, len(elements)):
            elements[0][i] += elements[j][i] * MODEL_WEIGHT[j]
        elements[0][i] /= sum(MODEL_WEIGHT)
    # avg_data = avg.read()
    # result.append(avg)
    F.save(elements[0], savePath, False)
