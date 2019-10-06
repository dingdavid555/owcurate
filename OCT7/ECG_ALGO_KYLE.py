# --------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------ PACKAGE IMPORT ----------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, lfilter
from datetime import datetime
from datetime import timedelta
import matplotlib.dates as mdates
from matplotlib.dates import strpdate2num, num2date, datestr2num
import statistics as stats
import pyedflib
import peakutils
import os
from scipy.signal import resample
from biosppy import storage
from biosppy.signals import ecg
from biosppy import utils
import csv

# Datetime formatting for X-axis on plots
xfmt = mdates.DateFormatter("%a @ %H:%M:%S:%f"[0:-3])  # Date as "<day of week> @ HH:MM:SS"
locator = mdates.HourLocator(byhour=[0, 3, 6, 9, 12, 15, 18, 21], interval=1)  # Tick marks every 3 hours

# --------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------- IN PROGRESS ---------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------


# add in retroactive non-wear period extension


def epoch_accel():

    t0_accelepoch = datetime.now()

    svm_list = []

    global epoch_svm
    epoch_svm = []

    # Calculates vector magnitude of every datapoint
    for x, y, z in zip(edf_file.accel_x, edf_file.accel_y, edf_file.accel_z):
        svm = round(((x**2 + y**2 + z**2)**(1/2) - 1000), 2)
        if svm < 0:  # Rounds to 0 if svm < 0
            svm_list.append(0)
        if svm >= 0:
            svm_list.append(svm)

    # Calculates epoch values
    for i in range(0, len(svm_list), edf_file.epoch_len*edf_file.signal_frequency_accel):
        start = i
        end = i + edf_file.epoch_len + edf_file.signal_frequency_accel - 1

        epoch_svm.append(round(sum(svm_list[start:end]), 2))

    # Calculates upstream epoch SD values (5-minute sliding window)
    global upstream_sd
    upstream_sd = []

    global upstream_below_thres
    upstream_below_thres = []

    for i in range(0, len(epoch_svm)):
        if i > len(epoch_svm) - 14:
            break

        sd_value = stats.stdev(epoch_svm[i:i+14])
        upstream_sd.append(round(sd_value, 2))

        # Codes as above/below threshold
        if sd_value <= 0.05:
            upstream_below_thres.append(1)
        if sd_value > 0.05:
            upstream_below_thres.append(0)

    t1_accelepoch = datetime.now()

    print("Accelerometer epoching complete. Took {} seconds.".format((t1_accelepoch-t0_accelepoch).seconds))


# epoch_accel()


def plot_nonwear():
    fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, sharex="col")
    ax1.plot(edf_file.raw_timestamps[::5], edf_file.ecg_filtered[::5], color="red")
    ax1.legend(loc="upper left", labels=["ECG"])

    ax2.plot(edf_file.accel_timestamps[::3], edf_file.accel_x[::3], color="blue")
    ax2.legend(loc="upper left", labels=["Accel_x"])

    ax3.plot(edf_file.epoch_timestamps[0:len(upstream_sd)], upstream_sd, color="orange")
    ax3.legend(loc="upper left", labels=["Upstream_SD"])
    ax3.axhline(y=0.05, color="black", linestyle="dashed")

    ax4.plot(edf_file.epoch_timestamps, edf_file.nonwear_final, color="black")
    ax4.legend(loc="upper left", labels=["NonWear"])

    plt.show()


# plot_nonwear()


# --------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------- GENERIC FUNCTIONS --------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------

# --------------------------------------------- PLOTS FOR BILL -------------------------------------------------------


def plot1(downsample, edf, ecg, title):

    print("\n" + "Generating plot #1...")

    fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, sharex="col", figsize=(12, 6))

    # Epoched data: epoch_timestamps and epoch_hr not always same length yet
    try:
        ax1.plot(ecg.epoch_timestamps[0:len(ecg.epoch_hr)], ecg.epoch_hr,
                 color="black", marker="o", markerfacecolor="red", markeredgecolor="black", markersize=4)
    except ValueError:
        ax1.plot(ecg.epoch_timestamps, ecg.epoch_hr[0:len(ecg.epoch_timestamps)],
                 color="black", marker="o", markerfacecolor="red", markeredgecolor="black", markersize=4)

    ax1.legend(loc="upper left", labels=["Epoch HR ({}-secs)".format(ecg.epoch_len)])
    ax1.set_ylim(-5, max(ecg.epoch_hr) * 1.1)
    ax1.set_ylabel("HR (bpm)")
    ax1.set_title(title)

    # Raw ECG
    ax2.plot(edf.raw_timestamps[0:len(edf.ecg_raw):downsample],
             edf.ecg_raw[::downsample], color="red")
    ax2.set_ylabel("Voltage (mV)")
    ax2.legend(loc="upper left", labels=["Raw ECG"])

    # Peak data and filtered ECG
    ax3.plot(edf.raw_timestamps[0:len(edf.ecg_filtered):downsample],
             edf.ecg_filtered[::downsample], color="black")

    ax3.plot([ecg.raw_timestamps[int(i / ecg.resample_factor)] for i in ecg.peak_indices_cor],
             [ecg.ecg_filtered[int(i / ecg.resample_factor)] for i in ecg.peak_indices_cor],
             linestyle="", marker="o", markerfacecolor="green", markeredgecolor="black", markersize=4)

    ax3.legend(loc="upper left", labels=["Filtered ECG", "Peaks (n={})".format(len(ecg.peak_indices_cor))])

    ax3.set_ylabel("Voltage (mV)")

    # Data that is fed into peak detection section of algorithm
    ax4.plot(ecg.accel_timestamps[::downsample], ecg.accel_x[::downsample], color="green")
    ax4.set_ylabel("Acceleration (mG)")
    ax4.legend(loc="upper left", labels=["Vertical Acceleration"])

    # Formatting
    plt.xticks(rotation=45, size=6)
    ax4.xaxis.set_major_formatter(xfmt)
    ax4.xaxis.set_major_locator(locator)

    plt.show()


def plot2(downsample, ecg, ankle, wrist, title):

    print("\n" + "Generating plot #2...")

    fig, (ax1, ax2, ax3) = plt.subplots(3, sharex="col", figsize=(12, 6))

    # HR
    try:
        ax1.plot(ecg.epoch_timestamps[0:len(ecg.epoch_hr)], ecg.epoch_hr,
                 color="black", marker="o", markerfacecolor="red", markeredgecolor="black", markersize=4)
    except ValueError:
        ax1.plot(ecg.epoch_timestamps, ecg.epoch_hr[0:len(ecg.epoch_timestamps)],
                 color="black", marker="o", markerfacecolor="red", markeredgecolor="black", markersize=4)

    ax1.legend(loc="upper left", labels=["Epoch HR ({}-secs)".format(ecg.epoch_len)])
    ax1.set_ylim(40, max(ecg.epoch_hr) * 1.1)
    ax1.set_ylabel("HR (bpm)")
    ax1.set_title(title)


    # Ankle acceleration
    ax2.plot(ankle.stamps[::downsample], ankle.accel_x[::downsample], color="#1D82BE")
    ax2.set_ylabel("Acceleration (mG)")
    ax2.legend(loc="upper left", labels=["Ankle Accel (AP)"])

    # Wrist acceleration
    ax3.plot(wrist.stamps[::downsample], wrist.accel_x[::downsample], color="green")
    ax3.set_ylabel("Acceleration (mG)")
    ax3.legend(loc="upper left", labels=["Wrist Accel (AP)"])

    # Formatting
    plt.xticks(rotation=45, size=6)
    ax3.xaxis.set_major_formatter(xfmt)
    ax3.xaxis.set_major_locator(locator)

    plt.show()


def plot3(downsample, edf, ankle, wrist, title):

    print("\n" + "Generating plot #3...")

    fig, (ax1, ax2, ax3) = plt.subplots(3, sharex="col", figsize=(12, 6))

    # Raw ECG
    ax1.plot(edf.raw_timestamps[0:len(edf.ecg_filtered):downsample],
             edf.ecg_filtered[::downsample], color="black")
    ax1.set_ylabel("Voltage (mV)")
    ax1.legend(loc="upper left", labels=["Filtered ECG"])
    ax1.set_title(title)

    # Ankle acceleration
    ax2.plot(ankle.stamps[::downsample], ankle.accel_x[::downsample], color="#1D82BE")
    ax2.set_ylabel("Acceleration (mG)")
    ax2.legend(loc="upper left", labels=["Ankle Accel (AP)"])

    # Wrist acceleration
    ax3.plot(wrist.stamps[::downsample], wrist.accel_x[::downsample], color="green")
    ax3.set_ylabel("Acceleration (mG)")
    ax3.legend(loc="upper left", labels=["Wrist Accel (AP)"])

    # Formatting
    plt.xticks(rotation=45, size=6)
    ax3.xaxis.set_major_formatter(xfmt)
    ax3.xaxis.set_major_locator(locator)

    plt.show()


def plot4(ecg, ankle, wrist, title):

    print("\n" + "Generating plot #4...")

    fig, (ax1, ax2, ax3) = plt.subplots(3, sharex="col", figsize=(12, 6))

    # HR
    try:
        ax1.plot(ecg.epoch_timestamps[0:len(ecg.epoch_hr)], ecg.epoch_hr,
                 color="black", marker="o", markerfacecolor="red", markeredgecolor="black", markersize=4)
    except ValueError:
        ax1.plot(ecg.epoch_timestamps, ecg.epoch_hr[0:len(ecg.epoch_timestamps)],
                 color="black", marker="o", markerfacecolor="red", markeredgecolor="black", markersize=4)

    ax1.legend(loc="upper left", labels=["Epoch HR ({}-secs)".format(ecg.epoch_len)])
    ax1.set_ylim(40, max(ecg.epoch_hr) * 1.1)
    ax1.set_ylabel("HR (bpm)")
    ax1.set_title(title)

    # Ankle accelerometer
    ax2.plot(ankle.stamps[0:len(ankle.epoch)*15*75:15*75], ankle.epoch, color="#1D82BE")
    ax2.set_ylabel("Activity counts")
    ax2.set_ylim(-5, max(ankle.epoch)*1.1)
    ax2.legend(loc="upper left", labels=["Ankle Accel (Epoched)"])

    # Wrist accelerometer
    ax3.plot(wrist.stamps[0:len(wrist.epoch)*15*75:15*75], wrist.epoch, color="green")
    ax3.set_ylim(-5, max(ankle.epoch)*1.1)
    ax3.set_ylabel("Activity counts")
    ax3.legend(loc="upper left", labels=["Wrist Accel (Epoched)"])

    # Formatting
    plt.xticks(rotation=45, size=6)
    ax3.xaxis.set_major_formatter(xfmt)
    ax3.xaxis.set_major_locator(locator)

    plt.show()


def plot5(downsample, ankle, wrist, title):

    print("\n" + "Generating plot #5...")

    fig, (ax1, ax2) = plt.subplots(2, sharex="col", figsize=(12, 6))

    # Ankle acceleration
    ax1.plot(ankle.stamps[::downsample], ankle.accel_x[::downsample], color="#1D82BE")
    ax1.set_ylabel("Acceleration (mG)")
    ax1.legend(loc="upper left", labels=["Ankle Accel (AP)"])
    ax1.set_title(title)

    # Wrist acceleration
    ax2.plot(wrist.stamps[::downsample], wrist.accel_x[::downsample], color="green")
    ax2.set_ylabel("Acceleration (mG)")
    ax2.legend(loc="upper left", labels=["Wrist Accel (AP)"])

    # Formatting
    plt.xticks(rotation=45, size=6)
    ax2.xaxis.set_major_formatter(xfmt)
    ax2.xaxis.set_major_locator(locator)

    plt.show()


def plot6(downsample, edf, title):

    # Raw ECG
    fig, (ax1, ax2) = plt.subplots(2, sharex="col", figsize=(12, 6))

    ax1.plot(edf.raw_timestamps[0:len(edf.ecg_raw):1], edf.ecg_raw[::1], color="red")
    ax1.set_ylabel("Voltage (mV)")
    ax1.legend(loc="upper left", labels=["Raw ECG"])
    ax1.set_title(title)

    # Filtered ECG
    ax2.plot(edf.raw_timestamps[0:len(edf.ecg_filtered):downsample], edf.ecg_filtered[::downsample], color="black")

    ax2.legend(loc="upper left", labels=["Filtered ECG"])

    ax2.set_ylabel("Voltage (mV)")

    # Formatting
    plt.xticks(rotation=45, size=6)
    ax2.xaxis.set_major_formatter(xfmt)
    ax2.xaxis.set_major_locator(locator)

    plt.show()


# --------------------------------------------- GENERIC FUNCTIONS -----------------------------------------------------

# def process_rr_hr(data):


def process_epochs(epoch_timestamps, beat_timestamps):
    """Calculates average HR in each epoch using epoch length and number of beats in that epoch."""

    t0_epoch = datetime.now()

    print("\n" + "Epoching HR data...")

    # Loops through epoch start timestamps
    epoch_start_stamp = []
    epoch_end_stamp = []
    epoch_beat_tally = []

    for epoch_start, epoch_end in zip(epoch_timestamps[:], epoch_timestamps[1:]):

        # Tally for number of beats in current epoch
        beat_tally = 0

        # End index of previous section: speeds up looping
        end_beat_index = 0

        # Loops through beat_timestamps and counts beats that fall within current epoch
        for beat_index, beat_stamp in enumerate(beat_timestamps[end_beat_index:]):

            if epoch_start <= beat_stamp < epoch_end:
                beat_tally += 1

            # Gets timestamps of first and last beats in epoch
            if beat_stamp >= epoch_end:
                epoch_start_stamp.append(beat_timestamps[beat_index - beat_tally])  # start timestamp

                if beat_tally != 0:
                    epoch_end_stamp.append(beat_timestamps[beat_index - 1])  # end timestamp
                    end_beat_index = beat_index - 1

                if beat_tally == 0:
                    epoch_end_stamp.append(epoch_end)  # end timestamp
                    end_beat_index = beat_index

        epoch_beat_tally.append(beat_tally)

    epoch_hr = []

    for start_stamp, stop_stamp, tally in zip(epoch_start_stamp, epoch_end_stamp, epoch_beat_tally):
        duration = (stop_stamp - start_stamp).seconds + (stop_stamp - start_stamp).microseconds / 1000000
        if duration == 0:
            print(duration)

        try:
            if tally >= 0:
                epoch_hr.append(round((tally - 1) * 60 / duration, 1))

            if tally == 0:
                epoch_hr.append(0)

        except ZeroDivisionError:
            pass

    t1_epoch = datetime.now()

    # Prints epoch HR data summary
    print("Epoched HR calculated. Took {} seconds.".format(round((t1_epoch - t0_epoch).seconds), 2))

    # returns epoch_hr so self.epoch_hr can be set
    return epoch_hr


def plot_data(algorithm_name, epoch_len, epoch_timestamps, epoch_hr, ecg_filtered, raw_timestamps, resample_factor,
              peak_indices_cor, peak_removed, accel_data, accel_timestamps):
    """Plots epoched HR, filtered data with detected peaks, and the data that is fed into the peak detection
       algorithm with detected peaks."""

    fig, (ax1, ax2, ax3) = plt.subplots(3, sharex="col")

    # Epoched data: epoch_timestamps and epoch_hr not always same length yet
    try:
        ax1.plot(epoch_timestamps[0:len(epoch_hr)], epoch_hr,
                 color="black", marker="o", markerfacecolor="red", markeredgecolor="black", markersize=4)
    except ValueError:
        ax1.plot(epoch_timestamps, epoch_hr[0:len(epoch_timestamps)],
                 color="black", marker="o", markerfacecolor="red", markeredgecolor="black", markersize=4)

    ax1.legend(loc="upper left", labels=["Epoch HR ({}-secs)".format(epoch_len)])
    ax1.set_ylim(40, max(epoch_hr)*1.1)
    ax1.set_ylabel("HR (bpm)")
    ax1.set_title("{} Algorithm".format(algorithm_name))

    # Peak data
    ax2.plot(raw_timestamps[0:len(ecg_filtered):3], ecg_filtered[::3], color="black")

    ax2.plot([raw_timestamps[int(i/resample_factor)] for i in peak_indices_cor],
             [ecg_filtered[int(i/resample_factor)] for i in peak_indices_cor],
             linestyle="", marker="o", markerfacecolor="green", markeredgecolor="black", markersize=4)

    ax2.plot([raw_timestamps[int(i/resample_factor)] for i in peak_removed],
             [ecg_filtered[int(i/resample_factor)] for i in peak_removed],
             linestyle="", marker="x", markeredgecolor="red", markersize=4)

    ax2.legend(loc="upper left", labels=["Filtered data", "Peaks (n={})".format(len(peak_indices_cor)),
                                         "False peaks (n={})".format(len(peak_removed))])

    ax2.set_ylabel("Voltage (mV)")

    # Data that is fed into peak detection section of algorithm
    ax3.plot(accel_timestamps, accel_data, color="green")
    ax3.set_ylabel("Acceleration (mG)")

    # Formatting
    plt.xticks(rotation=45, size=6)
    ax3.xaxis.set_major_formatter(xfmt)
    ax3.xaxis.set_major_locator(locator)

    plt.show()


def bandpass_filter(dataset, lowcut, highcut, signal_freq, filter_order):
    """Method that creates bandpass filter to ECG data."""

    # Filter characteristics
    nyquist_freq = 0.5 * signal_freq
    low = lowcut / nyquist_freq
    high = highcut / nyquist_freq
    b, a = butter(filter_order, [low, high], btype="band")
    y = lfilter(b, a, dataset)
    return y


def plot_epochs(algorithm_name, epoch_len, epoch_timestamps, epoch_hr):
    """Plots epoched HR, filtered data with detected peaks, and the data that is fed into the peak detection
       algorithm with detected peaks."""

    epoch_plot = plt.gca()

    # Epoched data
    plt.plot(epoch_timestamps[0:len(epoch_hr)], epoch_hr,
             color="black", marker="o", markerfacecolor="red", markeredgecolor="black", markersize=4)

    plt.ylim(-5, 180)
    plt.ylabel("HR (bpm)")
    plt.title("{} Algorithm: {}-sec epochs".format(algorithm_name, epoch_len))

    plt.xticks(rotation=45, size=6)
    epoch_plot.xaxis.set_major_formatter(xfmt)
    epoch_plot.xaxis.set_major_locator(locator)

    plt.show()


# --------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------ CLASS: EDF FILE ---------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------


class EdfFile:

    def __init__(self, file, crop, epoch_len, sliding_window_len, min_nonwear_duration):

        # Passes in arguments from call to class instance
        self.filename = file  # filename including full pathway
        self.file_id = self.filename.split(".", 1)[0]  # filename only, no extension

        self.epoch_len = epoch_len  # in seconds
        self.sliding_window_len = sliding_window_len  # length of windows for non-wear + high-amplitude detection
        self.crop = crop  # seconds to crop at start and end of file, list
        self.min_nw_dur = min_nonwear_duration

        self.raw_file = None  # object that stores EDF object

        self.signal_frequency = None  # sampling frequency of ECG, Hz
        self.signal_frequency_accel = None  # sampling frequency of accelerometer, Hz
        self.starttime = None  # timestamp of collection start
        self.collection_duration = None  # in seconds
        self.collection_duration_days = None  # in days

        self.load_time = None  # time it takes to load file

        self.ecg_raw = None  # raw ECG data
        self.ecg_filtered = None  # 1-35Hz, 2nd order bandpass filter
        self.raw_timestamps = None  # timestamps for each data point

        self.accel_x = None
        self.accel_y = None
        self.accel_z = None
        self.accel_timestamps = None

        # Signal quality data
        self.ecg_sd = None
        self.ecg_nonwear = None
        self.accel_nonwear = None
        self.ecg_highamp = None
        self.nonwear_final = []
        self.nonwear_start = []
        self.nonwear_end = []
        self.ecg_highamp_start = []
        self.ecg_highamp_end = []
        self.nonwear_duration = 0
        self.ecg_highamp_duration = 0

        self.epoch_timestamps = []  # timestamp for each epoch

        # Runs function
        self.load_edf()
        self.create_epochs()
        self.filter_ecg()
        # self.check_signal_quality()
        # self.calculate_lostdata_duration()
        # self.plot_signal_check()

        # self.plot_filtered()
        # self.create_epochs()

    def load_edf(self):
        """Loads ECG channel from EDF file and calculates timestamp for each datapoint. Crops time off beginning
           and end of file."""

        t0_load = datetime.now()

        print("\n" + "--------------------------------- Loading EDF file --------------------------------------")
        print("\n" + "Loading {} ...".format(self.file_id))

        # Reads in EDF file - ECG channel only
        self.raw_file = pyedflib.EdfReader(self.filename)

        # Reads in ECG channel only
        self.ecg_raw = np.zeros((1, self.raw_file.getNSamples()[0]))
        self.accel_x = self.raw_file.readSignal(chn=1)
        self.accel_y = self.raw_file.readSignal(chn=2)
        self.accel_z = self.raw_file.readSignal(chn=3)

        for datapoint in np.arange(1):
            self.ecg_raw[datapoint, :] = self.raw_file.readSignal(datapoint)

        # Reshapes raw ECG signal to long format
        self.ecg_raw = self.ecg_raw.reshape(self.ecg_raw.shape[1])

        # Reads in data from header
        self.signal_frequency = self.raw_file.getSampleFrequencies()[0]  # signal frequency of ECG
        self.signal_frequency_accel = self.raw_file.getSampleFrequencies()[1]  # signal frequency of accelerometer

        self.starttime = self.raw_file.getStartdatetime()  # start timestamp

        print("\n" + "Cropping first {} seconds and last {} seconds off of file.".format(self.crop[0], self.crop[1]))

        # Crops start and end of file
        if self.crop[0] != 0 or self.crop[1] != 0:

            self.starttime = self.starttime + timedelta(seconds=self.crop[0])

            self.ecg_raw = self.ecg_raw[self.crop[0]*self.signal_frequency:
                                        len(self.ecg_raw) - self.crop[1]*self.signal_frequency]

            self.accel_x = self.accel_x[self.crop[0]*self.signal_frequency_accel:
                                        len(self.accel_x) - self.crop[1]*self.signal_frequency_accel]

        # Duration of collection in seconds and days, respectively
        self.collection_duration = self.raw_file.file_duration - self.crop[0] - self.crop[1]  # in seconds

        self.collection_duration_days = self.collection_duration/3600/24  # in hours

        # Creates a timestamp for every data point
        self.raw_timestamps = [(self.starttime + timedelta(seconds=i / self.signal_frequency))
                               for i in range(0, len(self.ecg_raw))]

        self.accel_timestamps = [(self.starttime + timedelta(seconds=i / self.signal_frequency_accel))
                                 for i in range(0, len(self.accel_x))]

        print("\n" + "Data loaded. File duration is {} hours.".format(round(self.collection_duration / 3600), 1))

        t1_load = datetime.now()

        self.load_time = round((t1_load - t0_load).seconds, 1)

        print("Data import time is {} seconds.".format(self.load_time))

    def create_epochs(self):
        """Creates a list of timestamps corresponding to starttime + epoch_len."""

        # Creates list of timestamps corresponding to starttime + epoch_len for each epoch
        for i in range(0, int(self.collection_duration / self.epoch_len) + 1):
            timestamp = self.raw_timestamps[0] + timedelta(seconds=i * self.epoch_len)
            self.epoch_timestamps.append(timestamp)

    def filter_ecg(self):

        t0_filt = datetime.now()
        print("\n" + "Filtering data...")

        self.ecg_filtered = bandpass_filter(self.ecg_raw, lowcut=1, highcut=35,
                                            filter_order=2, signal_freq=self.signal_frequency)

        t1_filt = datetime.now()
        print("Filtering complete. Took {} seconds.".format(round((t1_filt-t0_filt).seconds), 2))

    def check_signal_quality(self):
        """Method that checks for periods of non-wear and unusable high-amplitude ECG signals."""

        t0_nonwear = datetime.now()
        print("\n" + "Running signal quality check algorithms...")

        # Generates numpy arrays of corresponding to number of epochs
        self.ecg_nonwear = np.zeros(int(len(self.ecg_filtered) / self.signal_frequency / self.sliding_window_len) + 1)
        self.accel_nonwear = np.zeros(int(len(self.accel_x) / self.signal_frequency_accel /
                                          self.sliding_window_len) + 1)
        self.ecg_sd = np.zeros(int(len(self.ecg_filtered) / self.signal_frequency / self.sliding_window_len) + 1)

        self.ecg_highamp = np.zeros(int(len(self.ecg_filtered) / self.signal_frequency / self.sliding_window_len) + 1)

        # Checks ECG data for periods of suspected non-wear and unusable data
        ecg_loop_index = 0

        for index in range(0, len(self.ecg_filtered), self.signal_frequency * self.sliding_window_len):
            start_index = index
            end_index = start_index + self.signal_frequency * self.sliding_window_len - 1

            if end_index > len(self.ecg_filtered):
                end_index = len(self.ecg_filtered)

            ecg_data_window = self.ecg_filtered[start_index:end_index]

            #self.ecg_sd[ecg_loop_index] = round(stats.stdev(ecg_data_window), 2)
            ecg_range = max(ecg_data_window) - min(ecg_data_window)

            # Checks range value compared to thresholds
            if ecg_range <= 175:
                self.ecg_nonwear[ecg_loop_index] = 1

            if ecg_range > 5000:
                self.ecg_highamp[ecg_loop_index] = 1

            ecg_loop_index += 1

            if end_index > len(self.ecg_filtered):
                break

        # Checks accelerometer for suspected non-wear periods
        accel_loop_index = 0

        for index in range(0, len(self.accel_x), self.signal_frequency_accel * self.sliding_window_len):
            start_index = index
            end_index = start_index + self.signal_frequency_accel * self.sliding_window_len - 1

            if end_index > len(self.accel_x):
                end_index = len(self.accel_x)

            accel_data_window = self.accel_x[start_index:end_index]

            accel_range = max(accel_data_window) - min(accel_data_window)

            if accel_range <= 50:
                self.accel_nonwear[accel_loop_index] = 1

            accel_loop_index += 1

            if end_index > len(self.accel_x):
                break

        # Checks where both ECG and accelerometer signals suggested non-wear periods
        for ecg, accel in zip(self.ecg_nonwear, self.accel_nonwear):
            if ecg == 1 and accel == 1:
                self.nonwear_final.append(1)
            else:
                self.nonwear_final.append(0)

        # Looks for min_nw_dur's worth of non-wear epochs to find non-wear periods
        loop_index = 0

        for i in self.nonwear_final:
            start_index = loop_index  # start of data segment
            end_index = int(loop_index + self.min_nw_dur * 60 / self.epoch_len)

            # Breaks if too close to end of file
            if end_index > len(self.nonwear_final):
                break

            # Does nothing if segment starts with worn device
            if self.nonwear_final[start_index] == 0:
                pass

            # Creates data segment if segment starts with non-wear
            if self.nonwear_final[start_index] == 1:
                current_data = self.nonwear_final[start_index:end_index]

                # Checks upstream epochs for wear status.
                # If half of data points in next min_duration period are non-wear,
                # continues scanning epoch-by-epoch starting at end of initial "current_data" block
                if sum(current_data) >= int(self.min_nw_dur * 60 / self.epoch_len / 2):
                    self.nonwear_start.append(self.epoch_timestamps[start_index])  # timestamp for start of period

                    scan_index = 1
                    keep_scanning = True

                    while keep_scanning:

                        if sum(self.nonwear_final[(end_index + scan_index):(end_index + scan_index + 5)]) > 0:
                            scan_index += 1
                            continue

                        # Breaks loop if wear epoch detected
                        # Adds end timestamp to nonwear_end
                        if sum(self.nonwear_final[(end_index + scan_index):(end_index + scan_index + 5)]) == 0:
                            try:
                                self.nonwear_end.append(self.epoch_timestamps[end_index + scan_index])
                            except IndexError:
                                self.nonwear_end.append(self.epoch_timestamps[-1])

                            loop_index = end_index + scan_index
                            keep_scanning = False
                            break

            loop_index += 1

        # Collapses consecutive non-wear periods if they are less than 1 minute apart
        for start, end in zip(self.nonwear_start[1:], self.nonwear_end[:]):
            if (start - end).seconds <= 60 * 5:
                self.nonwear_end.remove(end)
                self.nonwear_start.remove(start)

        t1_nonwear = datetime.now()
        print("Non-wear detection complete. Took {} seconds.".format(round((t1_nonwear-t0_nonwear).seconds, 1)))

    def calculate_lostdata_duration(self):
        """Calculates duration of all non-wear and periods where signal was lost."""

        for start, end in zip(self.nonwear_start, self.nonwear_end):
            period_dur = (end - start).seconds
            self.nonwear_duration += period_dur

        for start, end in zip(self.ecg_highamp_start, self.ecg_highamp_end):
            period_dur = (end - start).seconds
            self.ecg_highamp_duration += period_dur

    def plot_signal_check(self):

        print("\n" + "Generating plot of non-wear data...")

        fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, sharex="col")

        # Filtered data
        ax1.plot(self.raw_timestamps[::3], self.ecg_filtered[::3]/1000, color="black")
        ax1.set_ylabel("Filt. ECG (V)")

        # Accel_x
        ax2.plot(self.accel_timestamps[::2], self.accel_x[::2], color="green")
        ax2.set_ylabel("Accel_x (mG)")

        # Wear status
        ax3.plot(self.raw_timestamps[::self.sliding_window_len * self.signal_frequency], self.nonwear_final,
                 color="black", marker="o", markerfacecolor="red",
                 markeredgecolor="black")

        ax3.fill_between(self.raw_timestamps[::self.sliding_window_len * self.signal_frequency], 0, self.nonwear_final,
                         color="black")

        for start, end in zip(self.nonwear_start, self.nonwear_end):
            ax1.axvline(x=start, linestyle="dashed", color="green")
            ax1.axvline(x=end, linestyle="dashed", color="red")

        ax3.legend(loc="upper left", labels=["Wear status"])
        ax3.set_ylabel("Status")
        ax3.set_ylim(-0.05, 1.05)

        # High amplitude status
        ax4.plot(self.raw_timestamps[::self.sliding_window_len * self.signal_frequency], self.ecg_highamp,
                 color="black")
        ax4.fill_between(self.raw_timestamps[::self.sliding_window_len * self.signal_frequency], 0, self.ecg_highamp,
                         color="red")
        ax4.legend(loc="upper left", labels=["High amplitude status"])

        ax4.set_ylabel("Status")
        ax4.set_ylim(-0.05, 1.05)

        plt.show()

    def plot_filtered(self):

        print("\n" + "Generating graph of filtered ECG and accelerometer data...")

        fig, (ax1, ax2, ax3) = plt.subplots(3, sharex="col")

        ax1.plot(self.raw_timestamps[::3], self.ecg_raw[::3], color="red")
        ax1.set_ylabel("Voltage (mV)")
        ax1.legend(loc="upper left", labels=["Raw"])

        ax2.plot(self.raw_timestamps[::3], self.ecg_filtered[::3], color="black")
        ax2.set_ylabel("Voltage (mV)")
        ax2.legend(loc="upper left", labels=["1-35Hz BP Filter"])

        ax3.plot(self.accel_timestamps[::2], self.accel_x[::2], color="green")
        ax3.set_ylabel("Acceleration(mG)")
        ax3.legend(loc="upper left", labels=["Accel_x"])

        plt.xticks(rotation=45, size=6)
        ax3.xaxis.set_major_formatter(xfmt)
        ax3.xaxis.set_major_locator(locator)

        plt.show()


# --------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------- CLASS: PAIKRO SCRIPT -----------------------------------------------
# --------------------------------------------------------------------------------------------------------------------


class PaikroAlgorithm:

    def __init__(self, peak_detect_window, filter_stage, low_f, high_f, abs_thres, abs_thres_value):
        print("\n" + "------------------------------- Running Paikro Algorithm ----------------------------------")

        self.algorithm_name = "Paikro"
        self.epoch_len = edf_file.epoch_len
        self.peak_detect_window = peak_detect_window
        self.filter_stage = filter_stage
        self.low_f = low_f
        self.high_f = high_f
        self.abs_thres = abs_thres
        self.abs_thres_value = abs_thres_value
        self.resample_factor = 1

        self.file_id = edf_file.file_id
        self.signal_frequency = edf_file.signal_frequency
        self.starttime = edf_file.starttime
        self.collection_duration = edf_file.collection_duration

        self.ecg_raw = edf_file.ecg_raw[0:-1, ]
        self.raw_timestamps = edf_file.raw_timestamps
        self.accel_x = edf_file.accel_x
        self.accel_timestamps = edf_file.accel_timestamps

        self.ecg_deriv = None
        self.ecg_filtered = None
        self.ecg_squared = None
        self.peak_indices = None
        self.peak_indices_cor = []
        self.peak_values = None
        self.rr_intervals = []
        self.rr_hr = []

        self.peak_removed = []  # peaks that get removed in check process
        self.beat_timestamps = []
        self.epoch_hr = []
        self.epoch_timestamps = edf_file.epoch_timestamps
        self.epoch_start_stamp = []
        self.epoch_end_stamp = []
        self.epoch_beat_tally = []

        self.avg_hr = 0  # calculated from epoch_hr
        self.avg_rr_hr = 0  # calculated from beat-to-beat RR-intervals
        self.min_hr = 0
        self.max_hr = 0
        self.summary_data = {}

        # Runs methods
        self.run_paikro_algorithm()
        self.process_rr_hr()  # need to make generic
        self.epoch_hr = process_epochs(epoch_timestamps=self.epoch_timestamps, beat_timestamps=self.beat_timestamps)
        self.create_summary_data()

    @staticmethod
    def bandpass_filter(dataset, lowcut, highcut, signal_freq, filter_order):
        """Method that creates bandpass filter to ECG data."""

        # Filter characteristics
        nyquist_freq = 0.5 * signal_freq
        low = lowcut / nyquist_freq
        high = highcut / nyquist_freq
        b, a = butter(filter_order, [low, high], btype="band")
        y = lfilter(b, a, dataset)

        return y

    def run_paikro_algorithm(self):
        """1. Differentiates data using numpy's ediff1d function. 2. Squares the differentiated data. 3. Runs the peak
           detection."""

        # DIFFERENTIATION FUNCTION
        if self.filter_stage == "raw":
            t0_filt = datetime.now()

            ecg_data = self.ecg_raw

            print("\n" + "Filtering raw data ({}-{}Hz, 2nd order bandpass filter).".format(self.low_f, self.high_f))
            self.ecg_filtered = self.bandpass_filter(ecg_data,
                                                     lowcut=self.low_f, highcut=self.high_f, filter_order=2,
                                                     signal_freq=self.signal_frequency)

            t1_filt = datetime.now()

            print("Data has been filtered. Took {} seconds.".format(round((t1_filt - t0_filt).seconds), 2))

        t0_diff = datetime.now()

        print("\n" + "Differentiating raw ECG signal...")

        self.ecg_deriv = np.ediff1d(self.ecg_raw)

        t1_diff = datetime.now()

        print("ECG signal differentiated. Took {} seconds.".format(round((t1_diff-t0_diff).seconds), 2))

        # SQUARING FUNCTION
        """Squares filtered + differentiated data AND runs filtering method."""

        if self.filter_stage == "differentiated":
            t0_filt = datetime.now()

            ecg_data = self.ecg_deriv

            print("\n" + "Filtering differentiated data ({}-{}Hz, 2rd order bandpass filter).".
                  format(self.low_f, self.high_f))

            self.ecg_filtered = self.bandpass_filter(ecg_data,
                                                     lowcut=self.low_f, highcut=self.high_f, filter_order=2,
                                                     signal_freq=self.signal_frequency)

            t1_filt = datetime.now()

            print("Data has been filtered. Took {} seconds.".format(round((t1_filt-t0_filt).seconds), 2))

        t0_square = datetime.now()

        print("\n" + "Squaring data...")
        self.ecg_squared = self.ecg_filtered ** 2

        t1_square = datetime.now()
        print("Data has been squared. Took {} seconds.".format(round((t1_square-t0_square).seconds), 2))

        # PEAK DETECTION
        t0_peak = datetime.now()

        print("\n" + "Detecting QRS peaks...")

        # Peak detection using PeakUtils package with windowed data
        # Each window has its peaks detected independent of other windows
        for start_index in range(0, len(self.ecg_squared), self.signal_frequency * self.peak_detect_window):

            # Data section to use for current window
            current_data = [self.ecg_squared[start_index:(start_index + self.signal_frequency *
                                                          self.peak_detect_window - 1)]]

            # Detects peak in peak_detect_window number of seconds-long windows
            # min_dist set to 71ms (max detectable HR ~ 210 bpm)
            if not self.abs_thres:
                detected_peaks_indices = peakutils.indexes(current_data, thres=0.15,
                                                           min_dist=(int(self.signal_frequency / 3.5)))

            if self.abs_thres:
                detected_peaks_indices = peakutils.indexes(current_data, thres_abs=True, thres=self.abs_thres_value,
                                                           min_dist=(int(self.signal_frequency / 3.5)))

            # Corrects indices to account for previous window(s)
            detected_peaks_indices = detected_peaks_indices + start_index

            # Converts self.peak_indices to numpy array on first loop
            if start_index == 0:
                self.peak_indices = detected_peaks_indices

            # Concatenates new window peaks with existing peaks
            if start_index != 0:
                self.peak_indices = np.concatenate((self.peak_indices, detected_peaks_indices))

        # Gets squared ECG values of each peak
        self.peak_values = self.ecg_squared[self.peak_indices]

        t1_peak = datetime.now()

        print("QRS peaks detected. Found {} peaks. Took {} seconds.".format(len(self.peak_indices),
                                                                            round((t1_peak - t0_peak).seconds), 2))

    def process_rr_hr(self):
        """Calculates beat-to-beat HR using time between consecutive R-R intervals."""

        t0_rr = datetime.now()

        print("\n" + "Processing HR from consecutive RR-intervals...")

        # Calculates HR using converted time interval between QRS peak indices
        for beat1, beat2 in zip(self.peak_indices[:], self.peak_indices[1:]):
            # Does not use peaks less than 250ms apart
            if (beat2-beat1) > self.signal_frequency/4:
                self.peak_indices_cor.append(beat1)

                self.rr_hr.append(round(60 / ((beat2 - beat1) / self.signal_frequency), 1))
                self.rr_intervals.append((beat2 - beat1) / self.signal_frequency)

        self.avg_rr_hr = round(stats.mean(self.rr_hr), 1)

        # Converts indices to datetime timestamps using collection_starttime and sample frequency
        # Also removes peaks less than 333 ms apart (HR >= 180 bpm)
        for peak in self.peak_indices:
            self.beat_timestamps.append(self.starttime + timedelta(seconds=peak / self.signal_frequency))

        t1_rr = datetime.now()

        print("RR-interval HR processed. Took {} seconds.".format(round((t1_rr - t0_rr).seconds), 2))

    def create_summary_data(self):

        self.avg_hr = len(self.peak_indices_cor) * 60 / self.collection_duration

        self.summary_data.update({"filter (Hz)": [self.low_f, self.high_f]})
        self.summary_data.update({"avg_hr": round(self.avg_hr, 1)})
        self.summary_data.update({"n_peaks": len(self.peak_indices)})
        self.summary_data.update({"n_peaks_removed": len(self.peak_removed)})

    def plot_data(self):

        plot_data(algorithm_name=self.algorithm_name, epoch_len=self.epoch_len,
                  epoch_timestamps=self.epoch_timestamps, epoch_hr=self.epoch_hr,
                  ecg_filtered=self.ecg_filtered, raw_timestamps=self.raw_timestamps,
                  resample_factor=self.resample_factor,
                  peak_indices_cor=self.peak_indices_cor, peak_removed=self.peak_removed,
                  accel_data=self.accel_x, accel_timestamps=self.accel_timestamps)

    def plot_epochs(self):

        plot_epochs(algorithm_name=self.algorithm_name, epoch_len=self.epoch_len,
                    epoch_hr=self.epoch_hr, epoch_timestamps=self.epoch_timestamps)


# --------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------- CLASS: CHRISTOV ALGORITHM ------------------------------------------
# --------------------------------------------------------------------------------------------------------------------


class BiosppyAlgorithm:

    def __init__(self, edf_object, algorithm):
        """Able to run different algorithms from Biosppy.ecg package.
           See 'Canento, et al. (2012) Review and Comparison of Real Time Electrocardiogram Segmentation
           Algorithms for Biometric Application' for more details."""

        self.algorithm_name = algorithm
        print("\n" + "------------------------------- Running {} Algorithm ----------------------------------".
              format(self.algorithm_name))

        self.edf_object = edf_object
        self.epoch_len = self.edf_object.epoch_len
        self.resample_factor = 1

        self.file_id = self.edf_object.file_id
        self.signal_frequency = self.edf_object.signal_frequency
        self.starttime = self.edf_object.starttime
        self.collection_duration = self.edf_object.collection_duration

        self.biosspy_data = None
        self.ecg_raw = self.edf_object.ecg_raw[0:-1, ]
        self.ecg_filtered = None
        self.raw_timestamps = self.edf_object.raw_timestamps
        self.accel_x = self.edf_object.accel_x
        self.accel_timestamps = self.edf_object.accel_timestamps

        self.peak_indices = None
        self.peak_indices_cor = []
        self.peak_values = None
        self.rr_intervals = []
        self.rr_hr = []

        self.algorithm_data = None  # object for all data from algorithm
        self.peak_removed = []  # peaks that get removed in check process
        self.beat_timestamps = []
        self.epoch_hr = []
        self.epoch_timestamps = self.edf_object.epoch_timestamps
        self.epoch_start_stamp = []
        self.epoch_end_stamp = []
        self.epoch_beat_tally = []

        self.avg_hr = 0  # calculated from epoch_hr
        self.avg_rr_hr = 0  # calculated from beat-to-beat RR-intervals
        self.min_hr = 0
        self.max_hr = 0
        self.summary_data = {}

        # Runs methods
        self.run_ecg_algorithm()
        # self.process_rr_hr()  # need to make generic
        self.epoch_hr = process_epochs(epoch_timestamps=self.epoch_timestamps, beat_timestamps=self.beat_timestamps)
        self.create_summary_data()

    def run_ecg_algorithm(self):

        t0_peak = datetime.now()
        print("\n" + "Detecting QRS peaks...")

        self.biosspy_data = ecg.ecg(signal=self.ecg_raw, sampling_rate=self.signal_frequency, show=False)

        # A 5-20Hz, 300th order bandpass filter is applied in the biosppy.ecg.ecg package
        self.ecg_filtered = self.biosspy_data["filtered"]

        # Runs Christov algorithm
        if self.algorithm_name == "Christov":
            self.algorithm_data = ecg.christov_segmenter(signal=self.ecg_filtered,
                                                         sampling_rate=self.edf_object.signal_frequency)

        # Runs Engzee algorithm
        if self.algorithm_name == "Engzee":
            self.algorithm_data = ecg.engzee_segmenter(signal=self.ecg_filtered, threshold=0.25,
                                                       sampling_rate=self.edf_object.signal_frequency)

        # Runs Gamboa algorithm
        if self.algorithm_name == "Gamboa":
            self.algorithm_data = ecg.gamboa_segmenter(signal=self.ecg_filtered, sampling_rate=self.signal_frequency,
                                                       tol=0.05)

        # Runs Hamilton algorithm
        if self.algorithm_name == "Hamilton":
            self.algorithm_data = ecg.hamilton_segmenter(signal=self.ecg_filtered, sampling_rate=self.signal_frequency)

        # Saves peaks from algorithm to different object
        self.peak_indices = self.algorithm_data["rpeaks"]

        # Checks for peaks less than 300ms apart and removes them
        self.peak_indices_cor = ecg.correct_rpeaks(signal=self.ecg_filtered, rpeaks=self.peak_indices,
                                                   sampling_rate=self.signal_frequency, tol=0.150)["rpeaks"]

        # Finds peaks that were removed
        for i in self.peak_indices:
            if i not in self.peak_indices_cor:
                self.peak_removed.append(i)

        for peak in self.peak_indices:
            self.beat_timestamps.append(self.starttime + timedelta(seconds=peak / self.signal_frequency))

        t1_peak = datetime.now()
        print("QRS peaks detected. Found {} peaks. Took {} seconds.".format(len(self.peak_indices),
                                                                            round((t1_peak - t0_peak).seconds), 2))

    def create_summary_data(self):

        self.avg_hr = len(self.peak_indices_cor) * 60 / self.collection_duration

        self.summary_data.update({"filter (Hz)": ["5", "20"]})
        self.summary_data.update({"avg_hr": round(self.avg_hr, 1)})
        self.summary_data.update({"n_peaks": len(self.peak_indices)})
        self.summary_data.update({"n_peaks_removed": len(self.peak_removed)})

    def plot_epochs(self):

        plot_epochs(algorithm_name=self.algorithm_name, epoch_len=self.epoch_len,
                    epoch_hr=self.epoch_hr, epoch_timestamps=self.epoch_timestamps)

    def plot_data(self):

        plot_data(algorithm_name=self.algorithm_name, epoch_len=self.epoch_len,
                  epoch_timestamps=self.epoch_timestamps, epoch_hr=self.epoch_hr,
                  ecg_filtered=self.ecg_filtered, raw_timestamps=self.raw_timestamps,
                  resample_factor=self.resample_factor,
                  peak_indices_cor=self.peak_indices_cor, peak_removed=self.peak_removed,
                  accel_data=self.accel_x, accel_timestamps=self.accel_timestamps)

# --------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------- CLASS GENEACTIV FILE ---------------------------------------------
# --------------------------------------------------------------------------------------------------------------------


class AccelFile:

    def __init__(self, file, epoch_data):

        print("\n" + " --------------------------------- Loading accelerometer file ---------------------------------")

        self.filename = file
        self.epoch_data = epoch_data
        self.starttime = None
        self.stamps = []
        self.accel_x = None
        self.accel_y = None
        self.accel_z = None
        self.index_list = []
        self.svm = []
        self.step_peaks = []
        self.svm_peaks = None
        self.crop_list = []
        self.step_stamps = None
        self.x_steptimes = []
        self.end_indexes = []
        self.start_indexes = []
        self.epoch = []
        self.step_cadence = None

        self.import_data()

        if self.epoch_data:
            self.calculate_epoch_data()

        #self.detect_peaks()

    def import_data(self):

        print("\n" + "Loading GENEActiv file: {} ...".format(self.filename))

        if self.filename.split(".")[-1] != "bin":
            try:
                # Reads in timestamps and all 3 accel channels
                self.starttime, self.accel_x, self.accel_y, self.accel_z = np.loadtxt(fname=self.filename, delimiter=",",
                                                                        skiprows=100, usecols=(0, 1, 2, 3),
                                                                        dtype=str,
                                                                        converters={0: lambda x:
                                                                        num2date(strpdate2num("%Y-%m-%d %H:%M:%S:%f")
                                                                        ((x.decode("utf-8"))))}, unpack=True)

            except IndexError:
                self.starttime, self.accel_x = np.loadtxt(fname=self.filename, delimiter=",", skiprows=0,
                                                          usecols=(0, 1), unpack=True, dtype=str)

                self.accel_y = []
                self.accel_z = []

            # Formats first time stamp correctly
            self.starttime = datetime.strptime(self.starttime[0].split("+")[0], "%Y-%m-%d %H:%M:%S") + \
                             timedelta(microseconds=0)

        if self.filename.split(".")[-1] == "bin":
            self.accel_x = np.fromfile(file=self.filename, dtype=float, count=6480000)  # Reads in first 24 hours

            file_id = self.filename.split(".")[0].split("/")[-1].split("_")[2]
            self.starttime = datetime.strptime(starttime_dict[file_id], "%Y-%m-%d %H:%M:%S.%f")

            self.accel_y = []
            self.accel_z = []

        print("\n" + "Formatting timestamps...")

        self.stamps = [self.starttime + timedelta(microseconds=13333.3333 * i)
                       for i in range(len(self.accel_x))]

        # Creates list of timestamps since formatting wasn't working
        """for i in range(0, len(self.accel_x)):
            stamp = self.starttime + timedelta(seconds=i/75)
            self.stamps.append(datetime.strptime(datetime.strftime(stamp, "%Y-%m-%d %H:%M:%S.%f"),
                                                 "%Y-%m-%d %H:%M:%S.%f"))

            self.index_list.append(i)"""

        # Converts accel values from str to float
        self.accel_x = [round(float(i), 5) for i in self.accel_x]
        self.accel_y = [round(float(i), 5) for i in self.accel_y]
        self.accel_z = [round(float(i), 5) for i in self.accel_z]

        print("\n" + "File loaded.")

    def calculate_epoch_data(self):

        print("\n" + "Epoching data...")

        # Calculates vector magnitude of each sample
        for x, y, z in zip(self.accel_x, self.accel_y, self.accel_z):
            mag = (x**2 + y**2 + z**2)**0.5 - 1

            if mag < 0:
                self.svm.append(0)
            if mag >= 0:
                self.svm.append(mag)

        # Calculates SVM for 15-second epochs
        for i in range(0, len(self.svm), 75*15):

            if i+15*75 > len(self.svm):
                break

            svm_sum = sum(self.svm[i:i+15*75-1])
            self.epoch.append(round(svm_sum, 2))


# --------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------- RUNNING SCRIPT ---------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------

# High quality treadmill walk
control_edf = "OF_Bittium_HR.EDF"
control_ankle_file = "OF_GA_LAnkle.csv"
control_wrist_file = "OF_GA_LWrist.csv"

# Free-living test, 8 hours
freeliving_test = "Kyle_BF.EDF"

# PD
pd_wrist_file = "OND06_SBH_7595_01_SE01_GABL_GA_LWx.bin"
pd_ankle_file = "OND06_SBH_7595_01_SE01_GABL_GA_LAx.bin"

# ALS
als_ankle_file = "OND06_SBH_8448_01_SE01_GABL_GA_LAx.bin"
als_wrist_file = "OND06_SBH_8448_01_SE01_GABL_GA_LWx.bin"

if __name__ == "__main__":

    t0 = datetime.now()
    print("\n" + "Starting processing at {}.".format(datetime.strftime(t0, "%I:%M:%S %p")))

    # Treadmill walks
    control_edf = EdfFile(file=control_edf, crop=[5*60, 2*60], epoch_len=15,
                          sliding_window_len=15, min_nonwear_duration=5)
    control_ecg = BiosppyAlgorithm(edf_object=control_edf, algorithm="Christov")
    control_ankle = AccelFile(file=control_ankle_file, epoch_data=True)
    control_wrist = AccelFile(file=control_wrist_file, epoch_data=True)

    # Kyle's sample free-living data
    freeliving_test_edf = EdfFile(file=freeliving_test, crop=[5*60, 2*60],
                                  epoch_len=15, sliding_window_len=15, min_nonwear_duration=5)
    freeliving_test_ecg = BiosppyAlgorithm(edf_object=freeliving_test_edf, algorithm="Christov")

    starttime_dict = {"8448": "2019-07-17 11:50:00.000000",
                      "7595": "2019-06-04 12:00:00.000000"}
    pd_ankle = AccelFile(file=pd_ankle_file, epoch_data=False)
    pd_wrist = AccelFile(file=pd_wrist_file, epoch_data=False)
    als_ankle = AccelFile(file=als_ankle_file, epoch_data=False)
    als_wrist = AccelFile(file=als_wrist_file, epoch_data=False)

    t1 = datetime.now()
    print("\n" + "--------------------------------------------------------------------------------------- ")
    print("Program complete. Run time = {} seconds.".format(round((t1-t0).seconds), 2))


# --------------------------------------------------------------------------------------------------------------------
# --------------------------------------------- PLOTS FOR BILL -------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------

"""Highlight line of code (not including #) and press Shift+Alt+E to run."""

# ------------------------------------------ HEALTHY, TREADMILL WALK -------------------------------------------------
# HIGHLIGHT: ECG abnormalities at low intensity walks
# INFO: gait speeds 0.53 to 1.46 m/s

"""HR, Raw ECG, filtered ECG, Bittium acceleration"""
# plot1(downsample=3, edf=control_edf, ecg=control_ecg, title="Treadmill: healthy, young control")

"""HR, ankle acceleration, wrist acceleration"""
# plot2(downsample=3, ecg=control_ecg, wrist=control_wrist, ankle=control_ankle, title="Treadmill: healthy, young control")

"""Filtered ECG, ankle acceleration, wrist acceleration"""
# plot3(downsample=3, edf=control_edf, wrist=control_wrist, ankle=control_ankle, title="Treadmill: healthy, young control")

"""HR, ankle counts, wrist counts"""
# plot4(ecg=control_ecg, ankle=control_ankle, wrist=control_wrist, title="Treadmill: healthy, young control")

# ----------------------------------------------- SAMPLE FREE-LIVING -------------------------------------------------
#
# INFO: 8-hour collection on healthy 24-year old

"""HR, Raw ECG, filtered ECG, Bittium acceleration"""
# HIGHLIGHT: ECG algorithm fail --> section where HR drops around 1700 hours
# plot1(downsample=3, edf=freeliving_test_edf, ecg=freeliving_test_ecg, title="8 hours free-living: healthy, young control")

"""Raw and filtered ECG"""
# plot6(downsample=2, edf=freeliving_test_edf, title="8 hours free-living: healthy, young control")

# ----------------------------------------------- PARKINSON'S PATIENT ------------------------------------------------
# INFO: Parkinson's, shuffling gait
# HIGHLIGHT: 3am - perseveration in gait bouts

"""Ankle and wrist AP acceleration, 24-hour period"""
# plot5(downsample=3, ankle=pd_ankle, wrist=pd_wrist, title="24 hours free-living: Parkinson's Patient")

# -------------------------------------------------- ALS PATIENT -----------------------------------------------------
# INFO: ALS, limited arm use

"""Ankle and wrist AP acceleration, 24-hour period"""
# plot5(downsample=3, ankle=als_ankle, wrist=als_wrist, title="24 hours free-living: ALS (limited arm function)")
