
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

files = [LA_file, RA_file, RW_file]

try:
    with open(output_path+"Filtered.csv", 'r') as out:
        df = pd.read_csv(out, names=["SubjectID", "DeviceLocation", "StartTime", "EndTime"])
except IOError:
    print("IOERROR")
    with open(output_path+"Filtered.csv", 'w') as out:
        out.write("Index,SubjectID,DeviceLocation,StartTime,EndTime\n")
        df = pd.DataFrame(columns=["SubjectID", "Location", "StartTime", "EndTime"], index=["Index"])

summ = open(output_path+"Filtered.csv", 'a')
out = open(output_path+"Summary.csv", 'a')
j = 0
k = 0

for f in files:
    bin_file = f
    times = np.array([bin_file.fileInfo.start_time + timedelta(microseconds=13333.3333333 * i) for i in range(len(bin_file.x_channel))])
    svms = calculate_svms(bin_file.x_channel, bin_file.y_channel, bin_file.z_channel)
    filtered = filter_svms(svms)
    start_arr, end_arr = find_gaps(times, filtered)
    filt_start, filt_end = collapse_gaps(start_arr, end_arr, times, svms, 4, 5)
    start, end = temp_check(filt_start, filt_end, bin_file.temperatures, times)

    for i in range(len(start)):
        j += 1
        summ.write("%i,%s,%s,%s,%s\n" % (j, bin_file.fileInfo.subject_code,
                                        bin_file.fileInfo.location_code,
                                        start[i].strftime("%m/%d/%Y %H:%M:%S.%f"),
                                        end[i].strftime("%m/%d/%Y %H:%M:%S.%f")))

    for i in range(len(filt_start)):
        k += 1
        out.write("%i,%s,%s,%s,%s\n" % (k, bin_file.fileInfo.subject_code,
                                        bin_file.fileInfo.location_code,
                                        filt_start[i].strftime("%m/%d/%Y %H:%M:%S.%f"),
                                        filt_end[i].strftime("%m/%d/%Y %H:%M:%S.%f")))

out.close()
summ.close()
