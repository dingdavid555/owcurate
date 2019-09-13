import pyedflib
from owcurate.Python.Bittium.ReadBittiumEDF import *
from os import listdir, remove
from os.path import isfile, join
import pandas as pd
import numpy as np


path = input("Please enter input path: ")
working_dir = path + "\\Raw data\\Bittium\\"
output_dir = path + "\\Processed Data\\Bittium\\"
REDCap_dir = "\\Raw data\\REDCap\\"


files = [f for f in listdir(working_dir) if isfile(join(working_dir, f))]

try:
    with open(output_dir + "Summary.csv") as file:
        summary_df = pd.read_csv(file, names=["Index","Subject ID", "FileNameTest", "Frequency Test", "Notes"],
                                 header=0, index_col=["Index"])
except IOError:
    with open(output_dir+"Summary.csv", 'w') as file:
        file.write("Index,Subject ID,File Name Test,Frequency Test,Notes\n")
    summary_df = pd.DataFrame(columns=["Index", "Subject ID", "FileNameTest", "Frequency Test", "Notes"])

# Defining Constants
ECG_FREQUENCY = 250
ACC_FREQUENCY = 25


# Initializing REDCap files and database
REDCap_files = [f for f in listdir(path + REDCap_dir) if isfile(join(path + REDCap_dir, f))]
df_Baseline = pd.read_csv(path + REDCap_dir + REDCap_files[0])
df_Discharge = pd.read_csv(path + REDCap_dir + REDCap_files[1])


for f in files:
    curr_file = pyedflib.EdfReader(working_dir+f)
    frequencies = curr_file.getSampleFrequencies()
    curr_file_name = BittiumFileName(working_dir+f)
    notes = ""

    file_name_test = True
    frequency_test = True

    # running file name tests
    curr_file_name.arr[0] = curr_file_name.arr[0][-5:]
    curr_file_name.arr = curr_file_name.arr[0:3]
    file_name_to_test = "_".join(curr_file_name.arr)

    if file_name_to_test not in df_Baseline["subject_id"].values:
        notes += "Subject Code %s not in Baseline REDCap data\n" % file_name_to_test
        file_name_test = False
    if file_name_to_test not in df_Discharge["subject_id"].values:
        notes += "Subject Code %s not in Discharge REDCap data\n" % file_name_to_test
        file_name_test = False

    # Checking frequencies:
    if frequencies[0] != ECG_FREQUENCY:
        notes += "ECG Frequency mismatch: Expected: %i Actual %i\n" % (frequencies[0], ECG_FREQUENCY)
        file_name_test = False
    if frequencies[1] != ACC_FREQUENCY:
        notes += "X-channel Frequency mismatch: Expected: %i Actual %i\n" % (frequencies[1], ACC_FREQUENCY)
        file_name_test = False
    if frequencies[2] != ACC_FREQUENCY:
        notes += "Y-channel frequency mismatch: Expected: %i Actual %i\n" % (frequencies[2], ACC_FREQUENCY)
        file_name_test = False
    if frequencies[3] != ACC_FREQUENCY:
        notes += "Z-channel Frequency mismatch: Expected: %i Actual %i\n" % (frequencies[3], ACC_FREQUENCY)
        file_name_test = False

    if notes == "":
        notes = "No errors in file\n"

    output_array = [file_name_to_test, str(file_name_test), str(frequency_test), notes]
    summary_df.loc[len(summary_df)] = output_array
    curr_file._close()
    del curr_file

summary_df.duplicated(subset=["Subject ID"], keep='last')

remove(output_dir+"Summary.csv")

summary_df.to_csv(output_dir+"Summary.csv")