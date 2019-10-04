# David Ding - October 4th

# Imports
from Python.GENEActiv.non_wear_nostdev2 import *
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
# Live code for October 7th presentation

# Setting working directories
output_path = "C:\\Users\\y259ding\\Desktop\\presfiles\\Data\\"
input_path = "C:\\Users\\y259ding\\Desktop\\presfiles\\"

# Getting input (Header information) from the binary files
SampleLA = input_path + "OND07_WTL_3003_01_GA_LAnkle.bin"
SampleLW = input_path + "OND07_WTL_3003_01_GA_LWrist.bin"
SampleRA = input_path + "OND07_WTL_3003_01_GA_RAnkle.bin"
SampleRW = input_path + "OND07_WTL_3003_01_GA_RWrist.bin"
LA_file = ReadGENEActivBin(SampleLA)
LW_file = ReadGENEActivBin(SampleLW)
RA_file = ReadGENEActivBin(SampleRA)
RW_file = ReadGENEActivBin(SampleRW)

# Loading CSV Data
LA_file.x_channel = np.fromfile(input_path + "Data\\3003_left ankle_x-channel.bin")
LA_file.y_channel = np.fromfile(input_path + "Data\\3003_left ankle_y-channel.bin")
LA_file.z_channel = np.fromfile(input_path + "Data\\3003_left ankle_z-channel.bin")
LA_file.temperatures = np.fromfile(input_path + "Data\\3003_left ankle_temps.bin")

LW_file.x_channel = np.fromfile(input_path + "Data\\3003_left wrist_x-channel.bin")
LW_file.y_channel = np.fromfile(input_path + "Data\\3003_left wrist_y-channel.bin")
LW_file.z_channel = np.fromfile(input_path + "Data\\3003_left wrist_z-channel.bin")
LW_file.temperatures = np.fromfile(input_path + "Data\\3003_left wrist_temps.bin")

RA_file.x_channel = np.fromfile(input_path + "Data\\3003_right ankle_x-channel.bin")
RA_file.y_channel = np.fromfile(input_path + "Data\\3003_right ankle_y-channel.bin")
RA_file.z_channel = np.fromfile(input_path + "Data\\3003_right ankle_z-channel.bin")
RA_file.temperatures = np.fromfile(input_path + "Data\\3003_right ankle_temps.bin")

RW_file.x_channel = np.fromfile(input_path + "Data\\3003_left wrist_x-channel.bin")
RW_file.y_channel = np.fromfile(input_path + "Data\\3003_left wrist_y-channel.bin")
RW_file.z_channel = np.fromfile(input_path + "Data\\3003_left wrist_z-channel.bin")
RW_file.temperatures = np.fromfile(input_path + "Data\\3003_left wrist_temps.bin")

# Generating Timestamps. To graph, use matplotlib to graph times against whichever other params
times = np.array([LA_file.fileInfo.start_time + timedelta(microseconds=13333.333333 * i)
                  for i in range(len(LA_file.x_channel))])

# Getting filtered timestamps
filtered = pd.read_csv(input_path + "Data\\Filtered.csv")
LAnkle = filtered[filtered["DeviceLocation"] == "left ankle"]
RAnkle = filtered[filtered["DeviceLocation"] == "right ankle"]
LWrist = filtered[filtered["DeviceLocation"] == "left wrist"]
RWrist = filtered[filtered["DeviceLocation"] == "right wrist"]

LA_file.start_filt = LAnkle["StartTime"]
LA_file.end_filt = LAnkle["EndTime"]
RA_file.start_filt = RAnkle["StartTime"]
RA_file.end_filt = RAnkle["EndTime"]
LW_file.start_filt = LWrist["StartTime"]
LW_file.end_filt = LWrist["EndTime"]
RW_file.start_filt = RWrist["StartTime"]
RW_file.end_filt = RWrist["EndTime"]


temp_checked = pd.read_csv(input_path + "Data\\Summary.csv")
LAnkle = temp_checked[temp_checked["DeviceLocation"] == "left ankle"]
RAnkle = temp_checked[temp_checked["DeviceLocation"] == "right ankle"]
LWrist = temp_checked[temp_checked["DeviceLocation"] == "left wrist"]
RWrist = temp_checked[temp_checked["DeviceLocation"] == "right wrist"]

LA_file.start_filt = LAnkle["StartTime"]
LA_file.end_filt = LAnkle["EndTime"]
RA_file.start_filt = RAnkle["StartTime"]
RA_file.end_filt = RAnkle["EndTime"]
LW_file.start_filt = LWrist["StartTime"]
LW_file.end_filt = LWrist["EndTime"]
RW_file.start_filt = RWrist["StartTime"]
RW_file.end_filt = RWrist["EndTime"]

