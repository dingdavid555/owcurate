# YUHAO DAVID DING
# SEPTEMBER 6TH 2019
# GENERAL METHODS AND CLASSES FOR READING GENEACTIV FILES, USED FOR MODULARIZATION


# ============================= IMPORTS ==========================
import datetime
from datetime import *
import numpy as np
import pandas as pd


# ============================= CLASSES ==========================
# FileInfo is an object that stores the first parts of every file
class FileInfo:
    # =============== VARIABLE DECLARATION ===============
    # TODO: Commenting and documentation for these
    serial_code: int
    measurement_frequency: int
    measurement_period: int
    start_time: datetime
    config_time: datetime
    extract_time: datetime
    extract_notes: float
    location_code: str
    subject_code: int
    number_of_pages: int
    x_gain = int
    x_offset = int
    y_gain = int
    y_offset = int
    z_gain = int
    z_offset = int
    volts = int
    lux = int

    # =============== DEFINITIONS AND FUNCTIONS ===============
    def __init__(self, file):
        # Read in initial line to avoid the NULLError
        self.serial_code = -1
        self.measurement_frequency = -1
        self.measurement_period = -1
        self.start_time = ""
        self.config_time = ""
        self.extract_time = ""
        self.extract_notes = ""
        self.location_code = ""
        self.subject_code = -1
        self.number_of_pages = -1
        self.x_gain = -1
        self.y_gain = -1
        self.z_gain = -1
        self.x_offset = -1
        self.y_offset = -1
        self.z_offset = -1
        self.volts = -1
        self.lux = -1
        self.curr_line = file.readline()

        # Loop through the entire preview package to get the important information using "in" searching
        while True:
            # Finding serial code in the current lines
            if (self.serial_code == -1) and ("Serial Code" in self.curr_line):
                self.serial_code = int(self.curr_line[-6:])
                # print("Serial code:", self.serial_code)

            # Finding Measurement Frequency:
            if (self.measurement_frequency == -1) and ( "Measurement Frequency" in self.curr_line):
                index_of_colon = self.curr_line.index(":")
                index_of_H = self.curr_line.index("H")
                self.measurement_frequency = int(self.curr_line[index_of_colon + 1:index_of_H])
                # print("Measurement Frequency: ", self.measurement_frequency)

            # Finding Measurement Period
            if (self.measurement_period == -1) and ("Measurement Period" in self.curr_line):
                index_of_colon = self.curr_line.index(":")
                index_of_H = self.curr_line.index("H")
                self.measurement_period = int(self.curr_line[index_of_colon + 1:index_of_H])
                # print("Measurement Period: ", self.measurement_period, " Hours")

            # Finding Start time
            if (self.start_time == "") and ("Start Time" in self.curr_line):
                self.start_time = datetime.strptime(self.curr_line[self.curr_line.index(":") + 1: -1],
                                                    "%Y-%m-%d %H:%M:%S:%f")
                # print("Start Time: ", self.start_time)

            # Finding Config time
            if (self.config_time == "") and ("Config Time" in self.curr_line):
                self.config_time = datetime.strptime(self.curr_line[self.curr_line.index(":") + 1: -1],
                                                     "%Y-%m-%d %H:%M:%S:%f")
                # print("Config Time: ", self.config_time)

            # Finding Extract time
            if (self.extract_time == "") and ("Extract Time" in self.curr_line):
                self.extract_time = datetime.strptime(self.curr_line[self.curr_line.index(":") + 1: -1],
                                                      "%Y-%m-%d %H:%M:%S:%f")
                # print("Extract Time: ", self.extract_time)

            # Finding Extract Notes
            if (self.extract_notes == "") and ("Extract Notes" in self.curr_line):
                index_of_colon = self.curr_line.index(":")
                self.extract_notes = self.curr_line[index_of_colon + 1:-1]
                # print("Extract Notes (Time Drift): ", self.extract_notes)

            # Finding Location Code
            if (self.location_code == "") and ("Location Code" in self.curr_line):
                index_of_colon = self.curr_line.index(":")
                self.location_code = self.curr_line[index_of_colon + 1:-1]
                # print("Location of Device: ", self.location_code)

            # Finding Subject Code
            if (self.subject_code == -1) and ("Subject Code" in self.curr_line):
                index_of_colon = self.curr_line.index(":")
                self.subject_code = int(self.curr_line[index_of_colon + 1:index_of_colon + 5])
                # print("Subject Code: ", self.subject_code)

            # Finding Calibration Data
            if (self.x_gain == -1) and ("x gain" in self.curr_line):
                index_of_colon = self.curr_line.index(":")
                self.x_gain = int(self.curr_line[index_of_colon + 1: -1])
            if (self.y_gain == -1) and ("y gain" in self.curr_line):
                index_of_colon = self.curr_line.index(":")
                self.y_gain = int(self.curr_line[index_of_colon + 1: -1])
            if (self.z_gain == -1) and ("z gain" in self.curr_line):
                index_of_colon = self.curr_line.index(":")
                self.z_gain = int(self.curr_line[index_of_colon + 1: -1])
            if (self.x_offset == -1) and ("x offset" in self.curr_line):
                index_of_colon = self.curr_line.index(":")
                self.x_offset = int(self.curr_line[index_of_colon + 1: -1])
            if (self.y_offset == -1) and ("y offset" in self.curr_line):
                index_of_colon = self.curr_line.index(":")
                self.y_offset = int(self.curr_line[index_of_colon + 1: -1])
            if (self.z_offset == -1) and ("z offset" in self.curr_line):
                index_of_colon = self.curr_line.index(":")
                self.z_offset = int(self.curr_line[index_of_colon + 1: -1])
            if (self.volts == -1) and ("Volts" in self.curr_line):
                index_of_colon = self.curr_line.index(":")
                self.volts = int(self.curr_line[index_of_colon + 1: -1])
            if (self.lux == -1) and ("Lux" in self.curr_line):
                index_of_colon = self.curr_line.index(":")
                self.lux = int(self.curr_line[index_of_colon + 1: -1])

            # Finding Number of Pages
            if "Number of Pages" in self.curr_line:
                self.number_of_pages = int(self.curr_line[self.curr_line.index(":") + 1:-1])
                # print("Number of Pages: ", self.number_of_pages)
                break
            self.curr_line = file.readline()


# Data class is the script to hold each section of data as a unique object, available for parsing later
class Data:
    # =============== VARIABLE DECLARATION ===============
    # Data contains the following sources of data, extracted from the
    #   header files within each GENEActiv reader binary file
    # serial_code: the integer value for the device serial number
    # sequence_number: Which recording within the file this falls under
    # page_time: String data type for now, can be translated into a datetime type later
    # unassigned: NOT SURE WHAT THIS MEANS --> ASK
    # temperature: Recorded temperature in degrees Celsius
    # device_status: THESE SEEM ALL TO BE "Recording" ASK WHAT THIS DOES
    # measurement_frequency: what frequency the task is measured at
    # data: The long string of data to be parsed
    serial_code: int
    sequence_number: int
    page_time: str
    # unassigned: bool
    temperature: float
    battery_voltage: float
    device_status: str
    measurement_frequency: float
    data: str                        # This should be 3600 chars in length
    cleaned_data: np.array([])       # This will be initialized shortly

    # =============== DEFINITIONS AND FUNCTIONS ===============
    # Init function parses all the data required into the respective variables
    def __init__(self, file):
        self.file = file
        # This first "header_line" should always match up to be "Recorded Data"
        self.header_line = file.readline()

        # We read in the next line which should give the Serial Code
        # We now find the Serial Code
        self.curr_line, index_of_colon = self.read_next_line()
        self.serial_code = int(self.curr_line[index_of_colon + 1: -1])

        # Read another line, then find Sequence Number:
        self.curr_line, index_of_colon = self.read_next_line()
        self.sequence_number = int(self.curr_line[index_of_colon + 1: -1])

        # Finding page time:
        self.curr_line, index_of_colon = self.read_next_line()
        self.page_time = datetime.strptime(self.curr_line[index_of_colon + 1: -1],
                                           "%Y-%m-%d %H:%M:%S:%f")

        # Skipping "Unassigned"
        self.curr_line = file.readline()

        # Finding Temperature
        self.curr_line, index_of_colon = self.read_next_line()
        self.temperature = float(self.curr_line[index_of_colon + 1: -1])

        # Finding Battery Voltage
        self.curr_line, index_of_colon = self.read_next_line()
        self.battery_voltage = float(self.curr_line[index_of_colon + 1: -1])

        # Finding Device Status
        self.curr_line, index_of_colon = self.read_next_line()
        self.device_status = self.curr_line[index_of_colon + 1:-1]

        # Finding Measurement Frequency
        self.curr_line, index_of_colon = self.read_next_line()
        self.measurement_frequency = float(self.curr_line[index_of_colon + 1:-1])

        self.curr_line = file.readline()
        self.data = self.curr_line[:-1]

    # Quality of life function to return two parameters, first the line itself then the index of the colon
    # within the line
    def read_next_line(self):
        line = self.file.readline()
        return line, line.index(":")

    # Returns the entire object as an array, for DF use
    def flattened(self):
        # arr = [self.serial_code, self.sequence_number, self.page_time, self.temperature, self.battery_voltage,
        #        self.device_status, self.measurement_frequency, self.data]

        arr = [self.serial_code, self.sequence_number, self.page_time, self.temperature, self.data]
        return arr


# This class compounds the data together, used for further manipulation
class CompoundGENEActivData:
    def __init__(self, fileinfo, data):
        self.fileinfo = fileinfo
        self.data = data


# This is the class to read GENEActiv Binary Files
class ReadGENEActivBin:
    # Initialization
    def __init__(self, directory):
        # ============================ VARIABLES
        self.location = directory
        self.file = open(self.location, "r")
        self.file_instance_2 = open(self.location)
        self.fileInfo = FileInfo(self.file)
        self.InfoArray = [self.fileInfo.subject_code,
                          self.fileInfo.location_code,
                          self.fileInfo.serial_code,
                          self.fileInfo.measurement_frequency,
                          self.fileInfo.measurement_period,
                          self.fileInfo.start_time,
                          self.fileInfo.config_time,
                          self.fileInfo.extract_time,
                          self.fileInfo.extract_notes,
                          self.fileInfo.number_of_pages,
                          self.fileInfo.x_gain, self.fileInfo.x_offset,
                          self.fileInfo.y_gain, self.fileInfo.y_offset,
                          self.fileInfo.z_gain, self.fileInfo.z_offset,
                          self.fileInfo.volts, self.fileInfo.lux]
        self.actual_page_count = get_last_sequence_num(self.file_instance_2)
        self.file_instance_2.close()
        self.DataChunk = []
        self.x_channel = []
        self.y_channel = []
        self.z_channel = []
        self.temperatures = []
        self.curr_line = self.file.readline()
        for i in range(self.actual_page_count):
            curr_data_chunk = Data(self.file)
            self.DataChunk.append(curr_data_chunk.flattened())

        # print(self.DataChunk)

        self.fullData = CompoundGENEActivData(self.fileInfo, self.DataChunk)

        self.df = pd.DataFrame(data=self.DataChunk, columns=["Device Serial Code", "Sequence Number", "Page Time",
                                                             "Temperature", "Hexadecimal Data"])

    def parse_hex(self):
        for j, k in self.df.iterrows():
            curr_chunk = process_curr(k["Hexadecimal Data"], "", k["Sequence Number"], k["Page Time"],
                                      (self.fileInfo.x_offset, self.fileInfo.y_offset, self.fileInfo.z_offset),
                                      (self.fileInfo.x_gain, self.fileInfo.y_gain, self.fileInfo.z_gain))

            self.temperatures.append(k["Temperature"])
            for i in range(300):
                self.x_channel.append(curr_chunk[i][2])
                self.y_channel.append(curr_chunk[i][3])
                self.z_channel.append(curr_chunk[i][4])
                # print("%.5f%% done" % (k["Sequence Number"] * 100 / self.fileInfo.number_of_pages))


class GENEActivFileName:
    site: str
    subject_code: int
    visitNum: int
    location: str

    def __init__(self, f):
        self.arr = f.split("_")
        self.study = self.arr[0][-5:]
        self.site = self.arr[1]
        self.subject_code = int(self.arr[2])
        self.visitNum = int(self.arr[3])
        self.location = self.arr[len(self.arr)-1][:-4]


# ============================= DEFINITIONS
# get_last_sequence_num(f) gets the actual page count (ignores the header page count)
# f is a file object
def get_last_sequence_num(f):
    data = f.readlines()
    curr_str = data[-8]
    return int(curr_str[curr_str.index(":") + 1:]) + 1


def twos_comp(val, bits):
    if (val & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
        val = val - (1 << bits)        # compute negative value
    return val


# Process current file, this parses each current 4-second window
# input:x, output, iter, time:
def process_curr(x, output, iter, time, offsets, gains, write_to_file=False):
    # ======== VARIABLES
    #       x: the current line of raw hexadecimal code
    #       output: the file to output (CSV)
    #       iter: the current sequence number -> used for indexing
    #       time: the start time for this entry
    # x-arr is the array used for the raw hexadecimal strings split every 12 characters
    # returned_arr is the final output array in tuple form of (x_comp, y_comp, z_comp, time)
    # x_comp is the x-component of accelerometer data
    # y_comp is the y-component of accelerometer data
    # z_comp is the z-component of accelerometer data
    # curr is the current line that is going to be processed, must be unified to 48 length
    # light is the light levels
    # button is whether or not the button was pressed
    # res is the reserved slot
    # output_string is the final output string to be placed into the csv document
    x_arr = []
    returned_arr = []
    x_comp = None
    y_comp = None
    z_comp = None
    curr = None
    light = None
    button = None
    res = None
    output_string = ""
    x_offset, y_offset, z_offset = offsets
    x_gain, y_gain, z_gain = gains

    # First pre-process the data from the long hexadecimal string and parse every 12 characters
    for i in range(300):
        x_arr.append(x[i * 12: (i + 1) * 12])
    # Run through the x_arr array 300 times and process the data into component forms
    for j in range(300):
        # Update current values:
        curr = bin(int(x_arr[j], 16))[2:]
        curr = curr.zfill(48)
        x_comp = curr[0:12]
        y_comp = curr[12:24]
        z_comp = curr[24:36]
        light = curr[36:46]
        button = int(curr[46], 2)
        res = int(curr[47], 2)

        # run the twos component value on each composition which starts in binary form
        x_comp = twos_comp(int(x_comp, 2), 12)
        y_comp = twos_comp(int(y_comp, 2), 12)
        z_comp = twos_comp(int(z_comp, 2), 12)
        # run the modifiers as prescribed in the GENEActiv documentation
        x_comp = (x_comp * 100 - x_offset) / x_gain
        y_comp = (y_comp * 100 - y_offset) / y_gain
        z_comp = (z_comp * 100 - z_offset) / z_gain
        # update the time value based on 75Hz roughly (1000ms/75)
        time = time + timedelta(milliseconds=13.3333)

        if write_to_file:
            output_string = "%i, " % (iter * 300 + j) + time.strftime("%Y-%m-%d %H:%M:%S.%f") + ", %.3f, %.3f, %.3f\n" % (x_comp, y_comp, z_comp)
            output.write(output_string)

        returned_arr.append(((iter * 300) + j, time, x_comp, y_comp, z_comp))

    return returned_arr


