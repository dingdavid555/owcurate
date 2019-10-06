# David Ding - October 4th

# Imports
from Python.GENEActiv.non_wear_nostdev2 import *
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
# Live code for October 7th presentation


t0 = datetime.now()
# Setting working directories
output_path = "C:\\Users\\y259ding\\Desktop\\OND07\\Data\\"
input_path = "C:\\Users\\y259ding\\Desktop\\OND07\\"

# Getting input (Header information) from the binary files
SampleLA = input_path + "OND07_WTL_3001_02_GA_LAnkle.bin"
SampleRA = input_path + "OND07_WTL_3001_02_GA_RAnkle.bin"
SampleRW = input_path + "OND07_WTL_3001_02_GA_RWrist.bin"

LA_file = ReadGENEActivBin(SampleLA)
# LW_file = ReadGENEActivBin(SampleLW)
RA_file = ReadGENEActivBin(SampleRA)
RW_file = ReadGENEActivBin(SampleRW)

# Loading CSV Data
LA_file.x_channel = np.fromfile(input_path + "Data\\3001_left ankle_x-channel.bin")
LA_file.y_channel = np.fromfile(input_path + "Data\\3001_left ankle_y-channel.bin")
LA_file.z_channel = np.fromfile(input_path + "Data\\3001_left ankle_z-channel.bin")
LA_file.temperatures = np.fromfile(input_path + "Data\\3001_left ankle_temps.bin")

# LW_file.x_channel = np.fromfile(input_path + "Data\\3003_left wrist_x-channel.bin")
# LW_file.y_channel = np.fromfile(input_path + "Data\\3003_left wrist_y-channel.bin")
# LW_file.z_channel = np.fromfile(input_path + "Data\\3003_left wrist_z-channel.bin")
# LW_file.temperatures = np.fromfile(input_path + "Data\\3003_left wrist_temps.bin")

RA_file.x_channel = np.fromfile(input_path + "Data\\3001_right ankle_x-channel.bin")
RA_file.y_channel = np.fromfile(input_path + "Data\\3001_right ankle_y-channel.bin")
RA_file.z_channel = np.fromfile(input_path + "Data\\3001_right ankle_z-channel.bin")
RA_file.temperatures = np.fromfile(input_path + "Data\\3001_right ankle_temps.bin")

RW_file.x_channel = np.fromfile(input_path + "Data\\3001_right wrist_x-channel.bin")
RW_file.y_channel = np.fromfile(input_path + "Data\\3001_right wrist_y-channel.bin")
RW_file.z_channel = np.fromfile(input_path + "Data\\3001_right wrist_z-channel.bin")
RW_file.temperatures = np.fromfile(input_path + "Data\\3001_right wrist_temps.bin")

# Generating Timestamps. To graph, use matplotlib to graph times against whichever other params
times = np.array([LA_file.fileInfo.start_time + timedelta(microseconds=13333.333333 * i)
                  for i in range(len(LA_file.x_channel))])

# Getting filtered timestamps
filtered = pd.read_csv(input_path + "Data\\Summary.csv")
LAnkle = filtered[filtered["DeviceLocation"] == "left ankle"]
RAnkle = filtered[filtered["DeviceLocation"] == "right ankle"]
# LWrist = filtered[filtered["DeviceLocation"] == "left wrist"]
RWrist = filtered[filtered["DeviceLocation"] == "right wrist"]

LA_file.start_filt = LAnkle["StartTime"]
LA_file.end_filt = LAnkle["EndTime"]
RA_file.start_filt = RAnkle["StartTime"]
RA_file.end_filt = RAnkle["EndTime"]
# LW_file.start_filt = LWrist["StartTime"]
# LW_file.end_filt = LWrist["EndTime"]
RW_file.start_filt = RWrist["StartTime"]
RW_file.end_filt = RWrist["EndTime"]


temp_checked = pd.read_csv(input_path + "Data\\Filtered.csv")
LAnkle = temp_checked[temp_checked["DeviceLocation"] == "left ankle"]
RAnkle = temp_checked[temp_checked["DeviceLocation"] == "right ankle"]
# LWrist = temp_checked[temp_checked["DeviceLocation"] == "left wrist"]
RWrist = temp_checked[temp_checked["DeviceLocation"] == "right wrist"]

LA_file.start = LAnkle["StartTime"]
LA_file.end = LAnkle["EndTime"]
RA_file.start = RAnkle["StartTime"]
RA_file.end = RAnkle["EndTime"]
# LW_file.start = LWrist["StartTime"]
# LW_file.end = LWrist["EndTime"]
RW_file.start = RWrist["StartTime"]
RW_file.end = RWrist["EndTime"]

t1 = datetime.now()
print("Done Loading Files. Took {} seconds".format(round((t1-t0).seconds)))


def draw_Single_Accl(File):
    times = np.array([File.fileInfo.start_time + timedelta(microseconds=13333.33333 * i) for i in range(len(File.x_channel))])
    fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=(12, 8), sharex=True)

    # Plotting the X-accelerometer only
    ax1.plot(times[::3], File.x_channel[::3], linewidth=0.3)

    # Plotting the Temperature only
    ax2.plot(times[::300], File.temperatures, linewidth=0.3)

    # Plotting X-accelerometer with Filtered Gaps
    ax3.plot(times[::3], File.x_channel[::3], linewidth=0.3)
    filt_start = [datetime.strptime(j, "%m/%d/%Y %H:%M:%S.%f") for j in File.start_filt.to_list()]
    filt_end = [datetime.strptime(j, "%m/%d/%Y %H:%M:%S.%f") for j in File.end_filt.to_list()]
    for i in range(len(filt_start)):
        ax3.axvline(filt_start[i], -10, 10, c="red")
        ax3.axvline(filt_end[i], -10, 10, c="green")

    # Plotting X-accelerometer with Temperature Filtered Data
    ax4.plot(times[::3], File.x_channel[::3], linewidth=0.3)
    starts = [datetime.strptime(j, "%m/%d/%Y %H:%M:%S.%f") for j in File.start.to_list()]
    ends = [datetime.strptime(j, "%m/%d/%Y %H:%M:%S.%f") for j in File.end.to_list()]
    for i in range(len(File.start)):
        ax4.axvline(starts[i], -10, 10, c="red")
        ax4.axvline(ends[i], -10, 10, c="green")


# Best windows for Demonstration:
def best_case():
    fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=(12, 8), sharex=True)

    # Plotting the X-accelerometer only
    ax1.plot(times[::3], LA_file.x_channel[::3], linewidth=0.3)

    # Plotting the Temperature only
    ax2.plot(times[::300], LA_file.temperatures, linewidth=0.3)

    # Plotting X-accelerometer with Filtered Gaps
    ax3.plot(times[::3], LA_file.x_channel[::3], linewidth=0.3)
    filt_start = [datetime.strptime(j, "%m/%d/%Y %H:%M:%S.%f") for j in LA_file.start_filt.to_list()]
    filt_end = [datetime.strptime(j, "%m/%d/%Y %H:%M:%S.%f") for j in LA_file.end_filt.to_list()]
    for i in range(len(filt_start)):
        ax3.axvline(filt_start[i], -10, 10, c="red")
        ax3.axvline(filt_end[i], -10, 10, c="green")

    # Plotting X-accelerometer with Temperature Filtered Data
    ax4.plot(times[::3], LA_file.x_channel[::3], linewidth=0.3)
    starts = [datetime.strptime(j, "%m/%d/%Y %H:%M:%S.%f") for j in LA_file.start.to_list()]
    ends = [datetime.strptime(j, "%m/%d/%Y %H:%M:%S.%f") for j in LA_file.end.to_list()]
    for i in range(len(LA_file.start)):
        ax4.axvline(starts[i], -10, 10, c="red")
        ax4.axvline(ends[i], -10, 10, c="green")
