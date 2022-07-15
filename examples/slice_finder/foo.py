import numpy as np
import math

def accuracy_metric(label, output):
    res = [0]*len(label)
    for i in range(len(label)):
        if label[i] == output[i]:
            res[i] = 1
    res = [1-i for i in res]
    return (np.mean(res), np.std(res), len(res))