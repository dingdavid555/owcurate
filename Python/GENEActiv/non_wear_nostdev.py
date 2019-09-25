import numpy as np
import pandas as pd
from Python.GENEActiv.GENEActivReader import *
import matplotlib.pyplot as plt
import statistics
from math import *


def calculate_svms(x_channel, y_channel, z_channel):
    t0 = datetime.now()
    output_arr = np.zeros(len(x_channel))
    for i in range(len(x_channel)):
        output_arr[i] = sqrt(pow(x_channel[i], 2) + pow(y_channel[i], 2) + pow(z_channel[i], 2)) - 1
    t1 = datetime.now()
    print("Took {} seconds".format(round((t1-t0).seconds), 1))
    return output_arr


def calculate_svms_list(x_channel, y_channel, z_channel):
    t0 = datetime.now()
    output_arr = []
    for i in range(len(x_channel)):
        output_arr.append(sqrt(pow(x_channel[i], 2) + pow(y_channel[i], 2) + pow(z_channel[i], 2)) - 1)
    t1 = datetime.now()
    print("Took {} seconds".format(round((t1-t0).seconds), 1))
    return output_arr


def filter_svms(svm_array):
    output_arr = np.zeros(len(svm_array))
    for i in range(len(svm_array)):
        if svm_array[i] < 0.5:
            output_arr[i] = 0
        else:
            output_arr[i] = svm_array[i]
    return output_arr


def find_gaps(times, svm_array):
    start_array = []
    end_array = []
    curr_stat = False

    for i in range(len(svm_array)):
        if svm_array[i] == 0 and not curr_stat:
            start_array.append(times[i])
            curr_stat = True

        if svm_array[i] == 1 and curr_stat:
            end_array.append(times[i])
            curr_stat = False

    # Take out the first and last entries since there is a chance the sensor was not on the person
    start_array = start_array[1:-2]
    end_array = end_array[1:-1]
    output_arr = np.column_stack((start_array, end_array))

    return output_arr
