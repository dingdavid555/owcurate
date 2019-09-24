# DAVID DING
# September 23rd 2019
#

import pandas as pd
import numpy as np
from owcurate.Python.GENEActiv.GENEActivReader import *
import matplotlib.pyplot as plt
from matplotlib import style
import math
import statistics

WINDOWS = 5


def zip_channels(x_channel, y_channel, z_channel):
    output_arr= []
    for i in range(len(x_channel)):
        output_arr.append((x_channel[i], y_channel[i], z_channel[i]))
    return output_arr


def stdevs(x_channel, y_channel, z_channel, sample_size=75):
    output_arr = []
    for i in range(len(x_channel)//75):
        output_arr.append((statistics.stdev(x_channel[sample_size * i:sample_size * (i+1)]),
                           statistics.stdev(y_channel[sample_size * i:sample_size * (i+1)]),
                           statistics.stdev(z_channel[sample_size * i:sample_size * (i+1)])))
    return output_arr


def collapse_stdevs(arr_of_tuples):
    output_arr = []
    for i in range(len(arr_of_tuples)):
        output_arr.append((arr_of_tuples[i][0] + arr_of_tuples[i][1] + arr_of_tuples[i][2]) / 3)

    return output_arr


def is_stationary(movements, tolerance):
    stationary = 0
    for i in range(len(movements)):
        if movements[i] < tolerance:
            stationary += 1

    return stationary >= 0.75 * len(movements)


def error_correct_stationary(movements, window):
    length = len(movements)

    output_array = [[] for i in range(length - 1)]

    for i in range(length-window):
        if is_stationary(movements[i:i+window], 0.075):
            for j in range(window):
                output_array[i+j].append(0)
        else:
            for j in range(window):
                output_array[i+j].append(1)

    for i in range(len(output_array)):
        if output_array[i].count(0) >= 0.75 * len(output_array[i]):
            output_array[i] = 0
        else:
            output_array = 1
        # output_array[i] = statistics.mean(output_array[i])

    return output_array


# This returns an array of length
def start_end_times(arr_data):
    # TODO: THIS FUNCTION
    return 0


def pre_process(bin_file):
    bin_file.parse_hex()
    triaxial_stdev = stdevs(bin_file.x_channel, bin_file.y_channel, bin_file.z_channel)
    single_stdev = collapse_stdevs(triaxial_stdev)
    return error_correct_stationary(single_stdev)


'''t0 = datetime.now()
print("Loading File")
file = "O:\Data\ReMiNDD\Raw data\GENEActiv\OND06_SBH_1039_01_SE01_GABL_GA_LA.bin"
bin_file = ReadGENEActivBin(file)
t1 = datetime.now()

print("Done Loading File, took {} seconds".format(round((t1-t0).seconds), 2))

print("Parsing Hexadecimal: ")
bin_file.parse_hex()

t2 = datetime.now()
print("Done Parsing Hexadecimal, took {} seconds".format(round((t2-t1).seconds), 2))

print("Calculating Standard Deviations for 1-second windows: ")
movement_quotient = stdevs(bin_file.x_channel, bin_file.y_channel, bin_file.z_channel)
t3 = datetime.now()
print("Done calculating Standard Deviations. took {} seconds".format(round((t3-t2).seconds), 2))

print("Averaging Standard Deviations from tri-axial data: ")
single_stdev = collapse_stdevs(movement_quotient)
t4 = datetime.now()
print("Done, took {} seconds".format(round((t4-t3).seconds), 2))

print("Performing error checking")
prelim_checked = error_correct_stationary(single_stdev, 30)
t5 = datetime.now()
print("Done, took {} seconds".format(round((t5-t4).seconds), 2))

print("Plotting data...")
plt.plot(bin_file.x_channel)
# plt.plot([75*i for i in range(len(movement_quotient))], movement_quotient, ".")
plt.plot([75 * i for i in range(len(prelim_checked))], prelim_checked, ".")
t6 = datetime.now()

print("Program complete, took {} seconds".format(round((t6-t0).seconds), 2))

plt.show()'''