# ================================================================================
# DAVID DING
# SEPTEMBER 25TH 2019
# THIS FILE FINDS WEAR/NON-WEAR TIMES BASED ON A SERIES FILTERING CRITERIA
# ================================================================================


# ======================================== IMPORTS ========================================
import numpy as np
import pandas as pd
from owcurate.Python.GENEActiv.GENEActivReader import *
import matplotlib.pyplot as plt
import statistics
from math import *
from pandas.plotting import register_matplotlib_converters
from os import listdir, remove
from os.path import isfile, join

# ======================================== FUNCTION DEFINITIONS ========================================
# calculate_svms calculates the SVM (Sum of Vector Magnitudes) in each of the accelerometer's axis
# returns one list of all the SVM values for each sample
def calculate_svms(x_channel, y_channel, z_channel):
    t0 = datetime.now()
    output_arr = np.zeros(len(x_channel))
    for i in range(len(x_channel)):
        output_arr[i] = sqrt(pow(x_channel[i], 2) + pow(y_channel[i], 2) + pow(z_channel[i], 2)) - 1
    t1 = datetime.now()
    print("Done Calculating SVMs. Took {} seconds".format(round((t1-t0).seconds), 1))
    return output_arr


# filter_svms filters the small values (<0.5gs) to take on value of 0 for error checking
# returns an array of same length as inputted but of filtered data (Filter Process Part 1)
def filter_svms(svm_array):
    t0 = datetime.now()
    output_arr = np.zeros(len(svm_array))
    for i in range(len(svm_array)):
        if svm_array[i] < 0.5:
            output_arr[i] = 0
        else:
            output_arr[i] = svm_array[i]

    t1 = datetime.now()
    print("Done Filtering. Took {} seconds".format(round((t1-t0).seconds), 1))
    return output_arr


# find_gaps finds where in the svm_array(input) contains stretches of 0s in the filtered data
# returns the start and end indices of the gap periods (stationary activity) (Filter Process Part 2)
def find_gaps(times, svm_array):
    t0 = datetime.now()

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
    print("Done finding gaps. Took {} seconds".format(round((t1-t0).seconds), 1))
    print("%i gaps found" % len(start_array))

    return start_array, end_array


# collapse_gaps removes any gaps less than 1 minute in duration (Filter Process Part 3)
def collapse_gaps(start_array, end_array, times, svms, mins1, mins2):
    print("Starting with %i gaps" % len(start_array))
    t0 = datetime.now()
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

    t1 = datetime.now()
    print("Done Collapsing. Took {} seconds".format(round((t1 - t0).seconds), 1))

    return processed_start, processed_end


def temp_check(starts, ends, temperatures, times):
    t0 = datetime.now()

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

    t1 = datetime.now()
    print("Done Temperature Checks. Took {} seconds".format(round((t1 - t0).seconds), 1))

    return non_wear_start, non_wear_end


# ======================================== MAIN ========================================
# Runs through the Data Pipeline to process for non-wear time
# bin_file is the GENEActivBin Object that stores relevant information

register_matplotlib_converters()

output_dir = "O:\\Data\\ReMiNDD\\Processed Data\\GENEActiv\\Non-wear\\"
input_dir = "O:\\Data\\ReMiNDD\\Raw data\\GENEActiv"
files = [f for f in listdir(input_dir) if isfile(join(input_dir, f))]

for f in files:
    file = join(input_dir, f)
    df = pd.DataFrame(columns=["StartTime", "EndTime"])

    print("Initializing and Parsing Hexadecimal for %s" % file)
    bin_file = ReadGENEActivBin(file)
    bin_file.parse_hex()
    init_time = bin_file.fileInfo.start_time

    t0 = datetime.now()
    print("Generating Times")
    times = np.array([init_time + timedelta(microseconds=13333.3333333 * i) for i in range(len(bin_file.x_channel))])

    print("Calculating SVMs")
    svms = calculate_svms(bin_file.x_channel, bin_file.y_channel, bin_file.z_channel)

    print("Filtering SVMs")
    filtered = filter_svms(svms)

    # Initializing bin_file object instance
    print("Finding Gaps")
    start_arr, end_arr = find_gaps(times, filtered)

    print("Finding Standard Deviation of Gaps... this might take a while")
    filt_start, filt_end = collapse_gaps(start_arr, end_arr, times, svms, 4, 5)

    print("Conducting Temperature Checks")
    start, end = temp_check(filt_start, filt_end, bin_file.temperatures, times)

    # Percentage of non-wear

    t1 = datetime.now()

    print("Plotting...")
    fig, ax = plt.subplots(figsize=(10, 6))
    fig.autofmt_xdate()
    ax.set_title(file)
    ax.plot(times, bin_file.x_channel, "black", linewidth=0.3)

    for i in range(len(start)):
        ax.axvline(start[i], -10, 10, c="red")
        ax.axvline(end[i], -10, 10, c="green")

    plt.savefig(output_dir + f[:-4])

    total_len = timedelta()
    for j in range(len(start)):
        df.loc[j] = [start[j], end[j]]
        total_len += end[j] - start[j]

    total_time = timedelta(hours=bin_file.fileInfo.measurement_period)
    percent_non_wear = (total_len / total_time) * 100

    df.to_csv(output_dir + f[:-4] + ".csv")

    bin_file.file.close()

