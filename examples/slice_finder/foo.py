import numpy as np
import pickle
import math

def accuracy_metric(label, output):
    res = [0]*len(label)
    for i in range(len(label)):
        # print(label[i], output[i])
        if label[i] == output[i]:
            res[i] = 1
    res = [1-i for i in res]
    # print(np.mean(res))
    return (np.mean(res), np.std(res), len(res))

def accuracy_metric_audio(label, output):
    audio_dict = {0:'zero', 1:'one', 2:'two', 3:'three', 4:'four', 5:'five', 
            6:'six', 7:'seven', 8:'eight', 9:'nine'}

    res = [0]*len(label)
    for i in range(len(label)):
        if audio_dict[label[i][0]] == output[i][0]:
            res[i] = 1
    res = [1-i for i in res]
    return (np.mean(res), np.std(res), len(res))

