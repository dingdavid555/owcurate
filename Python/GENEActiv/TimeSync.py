from Python.GENEActiv.GENEActivReader import *
import pyedflib
import numpy as np
import pandas as pd
from os import chdir, listdir
from os.path import isfile, join
import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

'''
GENERAL IDEA:
GET CLOCK DRIFT IN SECONDS
DIVIDE TOTAL NUMBER OF SAMPLES BY CLOCK DRIFT TO SEE HOW OFTEN A SAMPLE SHOULD BE DELETED
THEN USE NP.DELETE WHILE GENERATING A NEW ARRAY/CHANNEL
GENERATE NEW TIMES
PLOT ACROSS ALL ACCELEROMETERS

'''

input_path = "/Users/nimbal/Documents/ReMiNDD/RawData/"
bin_path = "/Users/nimbal/Documents/ReMiNDD/ProcessedBIN/"
path_to_df = "/Users/nimbal/Documents/ReMiNDD/fileSummary/Summary.csv"


# Loading Variables
# Loading header information (not sure if needed since the df should store everything)
df = pd.read_csv(path_to_df)

# Loading each channel of accelerometer data
print("Reading files from input")
LA_x_channel = np.fromfile(bin_path + "8448_left ankle_x-channel.bin")
LA_y_channel = np.fromfile(bin_path + "8448_left ankle_y-channel.bin")
LA_z_channel = np.fromfile(bin_path + "8448_left ankle_z-channel.bin")
# LA_temperatures = np.fromfile(bin_path + "8448_left ankle_temps.bin")

LW_x_channel = np.fromfile(bin_path + "8448_left wrist_x-channel.bin")
LW_y_channel = np.fromfile(bin_path + "8448_left wrist_y-channel.bin")
LW_z_channel = np.fromfile(bin_path + "8448_left wrist_z-channel.bin")
# LW_temperatures = np.fromfile(bin_path + "8448_left wrist_temps.bin")


RA_x_channel = np.fromfile(bin_path + "8448_right ankle_x-channel.bin")
RA_y_channel = np.fromfile(bin_path + "8448_right ankle_y-channel.bin")
RA_z_channel = np.fromfile(bin_path + "8448_right ankle_z-channel.bin")
# RA_temperatures = np.fromfile(bin_path + "8448_right ankle_temps.bin")

RW_x_channel = np.fromfile(bin_path + "8448_right wrist_x-channel.bin")
RW_y_channel = np.fromfile(bin_path + "8448_right wrist_y-channel.bin")
RW_z_channel = np.fromfile(bin_path + "8448_right wrist_z-channel.bin")
# RW_temperatures = np.fromfile(bin_path + "8448_right wrist_temps.bin")

LA_time_shift = float(df.loc[49].ExtractNotes.split(" ")[-1][:-2])
LW_time_shift = float(df.loc[50].ExtractNotes.split(" ")[-1][:-2]) - 1.573333
RA_time_shift = float(df.loc[51].ExtractNotes.split(" ")[-1][:-2]) - 2.0893444333
RW_time_shift = float(df.loc[52].ExtractNotes.split(" ")[-1][:-2]) - 2.227777

LA_freq = df.loc[49].Frequency
LW_freq = df.loc[50].Frequency
RA_freq = df.loc[51].Frequency
RW_freq = df.loc[52].Frequency

LA_samples = df.loc[49].NumOfPages * LA_freq * 4
LW_samples = df.loc[50].NumOfPages * LW_freq * 4
RA_samples = df.loc[51].NumOfPages * RA_freq * 4
RW_samples = df.loc[52].NumOfPages * RW_freq * 4


LA_remove_counter = LA_samples / (LA_time_shift * LA_freq)
LW_remove_counter = LW_samples / (LW_time_shift * LW_freq)
RA_remove_counter = RA_samples / (RA_time_shift * RA_freq)
RW_remove_counter = RW_samples / (RW_time_shift * RW_freq)

print("Dropping Samples")
new_x_LA = np.delete(LA_x_channel, [(LA_remove_counter * i) for i in range(int(len(LA_x_channel) / LA_remove_counter))])
new_y_LA = np.delete(LA_y_channel, [(LA_remove_counter * i) for i in range(int(len(LA_y_channel) / LA_remove_counter))])
new_z_LA = np.delete(LA_z_channel, [(LA_remove_counter * i) for i in range(int(len(LA_z_channel) / LA_remove_counter))])

new_x_LW = np.delete(LW_x_channel, [(LW_remove_counter * i) for i in range(int(len(LW_x_channel) / LW_remove_counter))])
new_y_LW = np.delete(LW_y_channel, [(LW_remove_counter * i) for i in range(int(len(LW_y_channel) / LW_remove_counter))])
new_z_LW = np.delete(LW_z_channel, [(LW_remove_counter * i) for i in range(int(len(LW_z_channel) / LW_remove_counter))])


new_x_RA = np.delete(RA_x_channel, [(RA_remove_counter * i) for i in range(int(len(RA_x_channel) / RA_remove_counter))])
new_y_RA = np.delete(RA_y_channel, [(RA_remove_counter * i) for i in range(int(len(RA_y_channel) / RA_remove_counter))])
new_z_RA = np.delete(RA_z_channel, [(RA_remove_counter * i) for i in range(int(len(RA_z_channel) / RA_remove_counter))])

new_x_RW = np.delete(RW_x_channel, [(RW_remove_counter * i) for i in range(int(len(RW_x_channel) / RW_remove_counter))])
new_y_RW = np.delete(RW_y_channel, [(RW_remove_counter * i) for i in range(int(len(RW_y_channel) / RW_remove_counter))])
new_z_RW = np.delete(RW_z_channel, [(RW_remove_counter * i) for i in range(int(len(RW_z_channel) / RW_remove_counter))])



print("Generating Times") # This isn't used yet
# init_time_L = datetime.strptime(df.loc[49].StartTime, "%Y-%m-%d %H:%M:%S.%f")
# init_time_R = datetime.strptime(df.loc[51].StartTime, "%Y-%m-%d %H:%M:%S.%f")

# new_times_L = np.array([init_time_L + timedelta(microseconds=13333.33333 * i)
#                        for i in range(len(new_x_LA))])
# new_times_R = np.array([init_time_R + timedelta(microseconds=13333.33333 * i)
#                        for i in range(len(new_x_RA))])

print("Plotting")
fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=(10, 8), sharex=True)
ax1.plot(new_x_LA, linewidth=0.6)
ax1.set_title("Left Ankle")
ax2.plot(new_x_LW, linewidth=0.6)
ax2.set_title("Left Wrist")
ax3.plot(new_x_RA, linewidth=0.6)
ax3.set_title("Right Ankle")
ax4.plot(new_x_RW, linewidth=0.6)
ax4.set_title("Right Wrist")



