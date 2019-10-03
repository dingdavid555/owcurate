# ================================================================================
# DAVID DING
# SEPTEMBER 25TH 2019
# THIS FILE CONTAINS METHODS FOR THE WEAR/NON-WEAR TIMES
# ================================================================================


# ======================================== IMPORTS ========================================
import numpy as np
import pandas as pd
from Python.GENEActiv.GENEActivReader import *
import matplotlib.pyplot as plt
import statistics
from math import *
from pandas.plotting import register_matplotlib_converters
from os import listdir, remove
from os.path import isfile, join


# ======================================== FUNCTION DEFINITIONS ========================================
# calculate_svms calculates the SVM (Sum of Vector Magnitudes) in each of the accelerometer's axis
# returns one list of all the SVM values for each sample
# calculate_svms (list(float), list(float), list(float)) --> np.ndarray
def calculate_svms(x_channel, y_channel, z_channel):
    output_arr = np.zeros(len(x_channel))
    for i in range(len(x_channel)):
        output_arr[i] = sqrt(pow(x_channel[i], 2) + pow(y_channel[i], 2) + pow(z_channel[i], 2)) - 1
    return output_arr


# filter_svms filters the small values (<0.5gs) to take on value of 0 for error checking
# returns an array of same length as inputted but of filtered data (Filter Process Part 1)
# filter_svms (np.ndarray) --> np.ndarray
def filter_svms(svm_array):
    output_arr = np.zeros(len(svm_array))
    for i in range(len(svm_array)):
        if svm_array[i] < 0.5:
            output_arr[i] = 0
        else:
            output_arr[i] = svm_array[i]

    return output_arr


# find_gaps finds where in the svm_array(input) contains stretches of 0s in the filtered data
# returns the start and end indices of the gap periods (stationary activity) (Filter Process Part 2)
# find_gaps (np.ndarray, np.ndarray) --> np.ndarray
def find_gaps(times, svm_array):
    start_array = []
    end_array = []
    curr_stat = False

    for i in range(len(svm_array)):
        if svm_array[i] == 0 and not curr_stat:
            start_array.append(times[i])
            curr_stat = True

        if svm_array[i] > 0 and curr_stat:
            end_array.append(times[i])
            curr_stat = False

    # Take out the first and last entries since there is a chance the sensor was not on the person
    start_array = start_array[1:-2]
    end_array = end_array[1:-1]

    t1 = datetime.now()
    print("%i gaps found" % len(start_array))

    return start_array, end_array


# collapse_gaps removes any gaps less than 1 minute in duration (Filter Process Part 3)
def collapse_gaps(start_array, end_array, times, svms, mins1, mins2):
    # Duration Check
    new_start = []
    new_end = []
    for i in range(len(start_array)-1):
        if end_array[i] - start_array[i] > timedelta(minutes=mins1):
            new_start.append(start_array[i])
            new_end.append(end_array[i])
    print("After Duration check: %i gaps remaining" % len(new_start))

    # Standard Deviation Check
    stdev_checked_starts = []
    stdev_checked_ends = []
    for i in range(len(new_start)):
        start_index = int(np.where(times == new_start[i])[0])
        end_index = int(np.where(times == new_end[i])[0])
        curr_stdev = statistics.stdev(svms[start_index:end_index:15])
        print("Standard Deviation Number %i of %i has value %.5f"
              % (i, len(new_start), curr_stdev))

        if curr_stdev < 0.065:
            stdev_checked_starts.append(new_start[i])
            stdev_checked_ends.append(new_end[i])

    print("After STDev check: %i gaps remaining" % len(stdev_checked_starts))
    # Overlapping Window Check
    pre_process_start = []
    pre_process_end = []
    for i in range(len(stdev_checked_starts) - 1):
        if stdev_checked_ends[i + 1] >= stdev_checked_starts[i]:
            pre_process_start.append(stdev_checked_starts[i])
            pre_process_end.append(stdev_checked_ends[i])
    print("After Overlapping Window Checks: %i gaps remaining" % len(pre_process_start))

    processed_start = []
    processed_end = []
    for i in range(len(pre_process_start) - 1):
        if pre_process_start[i + 1] - pre_process_end[i] > timedelta(minutes=mins2):
            processed_start.append(pre_process_start[i])
            processed_end.append(pre_process_end[i])
    print("After Ending Window Check: %i gaps remaining" % len(processed_start))

    return processed_start, processed_end


# temp_check checks the linear regression slope for the temperatures between gaps
def temp_check(starts, ends, temperatures, times):
    non_wear_start = []
    non_wear_end = []
    curr_temps = []

    for i in range(len(starts)):
        start_index = int(np.where(times == starts[i])[0])//300
        end_index = int(np.where(times == ends[i])[0])//300
        indices = np.array([j for j in range(start_index, end_index, 5)])
        curr_temps = np.array(temperatures[start_index:end_index:5])
        m = (statistics.mean(curr_temps) * statistics.mean(indices) - statistics.mean(curr_temps * indices))
        print("Starting from %s has value %.5f" % (starts[i].strftime("%H:%M:%S"), m))

        if m > 15:
            non_wear_start.append(starts[i])
            non_wear_end.append(ends[i])

    print("After Temperature Checking: %i periods of potential non-wear remaining" % len(non_wear_start))

    return non_wear_start, non_wear_end
