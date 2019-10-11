# David Ding
# October 9th 2019
# Bittium PDF Creation Tool

# Imports
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
import pyedflib
import datetime
from fpdf import FPDF
from os import listdir, remove
from os.path import isfile, join

class BittiumObject():
    def __init__(self, path):
        # VARIABLES
        # file is the EdfReader file
        # starttime is the datetime object for the start of the sampling duration
        # header_df stores all the signal labels in a dataframe with the following specifications:
        #           Index : Label Name : Number of Samples : Signal Frequency
        # ECG_times are the list of datetime objects that correspond to each sample of the ECG data
        # accl_times are the list of datetime objects that correspond to each sample of the acceleration data
        # ECG is the numpy array that gets the ECG data
        # x_accl is a numpy array that stores the x-acceleration channel data
        # y_accl, z_accl follows from x_accl for their respective axis
        self.file = pyedflib.EdfReader(path)
        self.filename = path.split("/")[-1]
        self.starttime = self.file.getStartdatetime()
        self.subjectID = int(path.split("_")[2])
        self.frequencies = None
        self.samples = None
        self.labels = None
        self.header_df = None
        self.ECG_times = None
        self.accl_times = None
        self.ECG = None
        self.x_accl = None
        self.y_accl = None
        self.z_accl = None

    # Reads header information including information about each channel's own respective headers
    def read_header(self):
        self.frequencies = self.file.getSampleFrequencies()
        self.samples = self.file.getNSamples()
        self.labels = self.file.getSignalLabels()
        self.header_df = pd.DataFrame(data=list(zip(self.labels,
                                                    self.samples,
                                                    self.frequencies)),
                                      columns=["LabelNames", "NumofSamples", "SignalFrequency"])

    # Reads signals from each respective channel
    def read_signals(self):
        self.ECG_times = np.array([self.starttime + datetime.timedelta(seconds=i/self.frequencies[0])
                                   for i in range(self.samples[0])])
        self.accl_times = np.array([self.starttime + datetime.timedelta(seconds=i/self.frequencies[1])
                                    for i in range(self.samples[1])])
        self.ECG = self.file.readSignal(0)
        self.x_accl = self.file.readSignal(1)
        self.y_accl = self.file.readSignal(2)
        self.z_accl = self.file.readSignal(3)

    # Plots ECG, X, Y, Z stacked from sample a to sample b
    def plot_all_stacked(self):
        fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=(12, 8), sharex=True)
        ax1.plot(self.ECG_times, self.ECG, linewidth=0.3)
        ax2.plot(self.accl_times, self.x_accl, linewidth=0.3)
        ax3.plot(self.accl_times, self.y_accl, linewidth=0.3)
        ax4.plot(self.accl_times, self.z_accl, linewidth=0.3)
        fig.autofmt_xdate()

    # plots acceleration in intervals with a user-specified starting time and interval length
    # start is starting time (in minutes)
    # interval is the duration (in minutes)
    def plot_accl_interval(self, start=0, interval=240):
        num_of_intervals = (self.samples[1] - start * self.frequencies[1]) // (self.frequencies[1] * interval * 60)
        start_sample = start * self.frequencies[1]
        interval_of_sample = interval * self.frequencies[1] * 60
        for i in range(num_of_intervals):
            fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(8, 3), sharex=True)
            ax1.plot(self.accl_times[start_sample:start_sample + interval_of_sample],
                     self.x_accl[start_sample:start_sample + interval_of_sample], linewidth=0.3)
            ax2.plot(self.accl_times[start_sample:start_sample + interval_of_sample],
                     self.y_accl[start_sample:start_sample + interval_of_sample], linewidth=0.3)
            ax3.plot(self.accl_times[start_sample:start_sample + interval_of_sample],
                     self.z_accl[start_sample:start_sample + interval_of_sample], linewidth=0.3)
            start_sample += interval_of_sample
            plt.savefig("Interval_%i.png" % i)
            plt.close()

        # Plot the last iteration
        end_sample = self.samples[1]
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(8, 3), sharex=True)
        ax1.plot(self.accl_times[start_sample:end_sample],
                 self.x_accl[start_sample:end_sample], linewidth=0.3)
        ax2.plot(self.accl_times[start_sample:end_sample],
                 self.y_accl[start_sample:end_sample], linewidth=0.3)
        ax3.plot(self.accl_times[start_sample:end_sample],
                 self.z_accl[start_sample:end_sample], linewidth=0.3)
        plt.savefig("Last_Interval.png")
        plt.close()

    def plot_ecg_interval(self, start=0, interval=240, window_len=15):
        num_of_intervals = (self.samples[0] - start * self.frequencies[0]) // (self.frequencies[0] * interval * 60)
        start_sample = start * self.frequencies[0]
        interval_of_sample = interval * self.frequencies[0]
        x_axis = np.array([datetime.datetime.now() + datetime.timedelta(seconds=i / self.frequencies[0])
                           for i in range(self.frequencies[0] * window_len)])

        for i in range(num_of_intervals):
            fig, ax = plt.subplots(1, 1, figsize=(8, 4))
            inner_sample_num = start_sample

            for k in range(10):
                ECGSamples = self.ECG[inner_sample_num: inner_sample_num + self.frequencies[0] * window_len]
                max_val = max(ECGSamples)
                min_val = min(ECGSamples)
                values = np.array([((j - min_val) / (max_val - min_val)) + k for j in ECGSamples])

                ax.plot(x_axis, values, linewidth=0.3)
                inner_sample_num += (interval // 10) * self.frequencies[0]

            start_sample += interval_of_sample
            print("ECG_Interval_%i.png outputted" % i)
            plt.savefig("ECG_Interval_%i.png" % i)
            plt.show()
            plt.close()

    def generate_pdf(self, start=0, interval=240, window_len=15):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Courier", size=12)
        output_string = "Subject ID: %i\n" % self.subjectID
        for index, row in self.header_df.iterrows():
            output_string += "Channel:%s Len: %s Freq: %s\n" % \
                             (row["LabelNames"], row["NumofSamples"], row["SignalFrequency"])

        pdf.multi_cell(400, 5, output_string, align='L')

        num_of_intervals = (self.samples[0] - start * self.frequencies[0]) // (self.frequencies[0] * interval * 60)

        for i in range(num_of_intervals):
            pdf.add_page()
            pdf.image("Interval_%i.png" % i, x=1, y=1, w=200, h=80, type='png')
            remove("Interval_%i.png" % i)
            pdf.image("ECG_Interval_%i.png" % i, x=1, y=100, w=200, h=100, type='png')
            remove("ECG_Interval_%i.png" % i)

        pdf.output(self.filename[:-4] + ".pdf")



bit = BittiumObject("/Volumes/nimbal$/Data/ReMiNDD/Raw data/Bittium/OND06_SBH_1039_01_SE01_GABL_BF_02.EDF")
bit.read_header()
bit.read_signals()
bit.plot_accl_interval()
bit.plot_ecg_interval()
bit.generate_pdf()




