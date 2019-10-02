# DAVID DING
# SEPTEMBER 12TH 2019
# This program generates a summary csv for each folder based on various checks for file integrity
# WORK IN PROGRESS

# ======================================== IMPORTS =============================
from owcurate.Python.GENEActiv.GENEActivReader import *
import pandas as pd
from os import listdir, remove
from os.path import isfile, join


# ======================================== DEFINITIONS AND CLASSES
def process_location(str1, str2):
    location_sets = {"la": ['left ankle', 'lankle', 'la'],
                     "ra": ['right ankle', 'rankle', 'ra'],
                     "lw": ['left wrist', 'lwrist', 'lw'],
                     "rw": ['right wrist', 'rwrist', 'rw']}
    try:
        result = str2.lower() in location_sets[str1.lower()]
    except KeyError:
        result = False
    return result


# ======================================== Reading files in and generating main DB
# Variables to start loading files
path = input("Please enter the file path: ")
in_path = '\\Raw data\\GENEActiv\\'
origin = path + in_path
out_path = "\\Processed Data\\GENEActiv\\"
destination = path + out_path
REDCap_dir = "\\Raw data\\REDCap\\"

# All the files to check
files_to_check = [f for f in listdir(origin) if (isfile(join(origin, f)) and (".bin" in f))]
curr_file_name = None
curr_file_info = None

try:
    with open(destination + "Summary.csv") as file:
        summary_df = pd.read_csv(file, names=["Index", "Subject ID", "FileNameTest", "Frequency Test",
                                              "Page Count Test", "Location Test", "Notes"],
                                 header=0, index_col=["Index"])
except IOError:
    with open(destination+"Summary.csv", 'w') as file:
        file.write("Index,Subject ID,File Name Test,Frequency Test,Page Count Test,Location Test,Notes\n")
    summary_df = pd.DataFrame(columns=["Subject ID", "FileNameTest", "Frequency Test",
                                       "Page Count Test", "Location Test", "Notes"], index=["Index"])

# ================ CONSTANTS TO CHECK AGAINST
MEASUREMENT_FREQUENCY = 75


REDCap_files = [f for f in listdir(path + REDCap_dir) if isfile(join(path + REDCap_dir, f))]
df_Baseline = pd.read_csv(path + REDCap_dir + REDCap_files[0])
df_Discharge = pd.read_csv(path + REDCap_dir + REDCap_files[0])


for f in files_to_check:
    curr_file_info = ReadGENEActivBin(origin+f)
    curr_file_name = GENEActivFileName(origin+f)
    notes = ""

    # Resetting boolean parameters for outputs
    file_name_test = True
    frequency_test = True
    page_count_test = True
    sensor_location_test = True

    # ================== Checking File names:
    if curr_file_name.subject_code != curr_file_info.fileInfo.subject_code:
        notes += "Subject Code Discrepancy: FileName: %i Binary File Info: %i\n"%(curr_file_name.subject_code,
                                                                                  curr_file_info.fileInfo.subject_code)
        file_name_test = False

    # processing file_name for redcap data
    curr_file_name.arr[0] = curr_file_name.arr[0][-5:]
    curr_file_name.arr = curr_file_name.arr[0:3]
    file_name_to_test = "_".join(curr_file_name.arr)

    if file_name_to_test not in df_Baseline["subject_id"].values:
        notes += "Subject Code %s not in Baseline REDCap data\n" % file_name_to_test
        file_name_test = False
    if file_name_to_test not in df_Discharge["subject_id"].values:
        notes += "Subject Code %s not in Discharge REDCap data\n" % file_name_to_test
        file_name_test = False

    # =============== Checking FileInfo
    if curr_file_info.fileInfo.measurement_frequency != MEASUREMENT_FREQUENCY:
        notes += "Measurement Frequency does not match expected value. Expected: %i. Actual: %i\n" \
                 % (MEASUREMENT_FREQUENCY, curr_file_info.fileInfo.measurement_frequency)
        frequency_test = False

    if curr_file_info.actual_page_count != curr_file_info.fileInfo.number_of_pages:
        notes += "Number of pages recorded does not match actual number of pages. Expected: %i. Actual: %i\n" % \
                 (curr_file_info.fileInfo.number_of_pages, curr_file_info.actual_page_count)
        page_count_test = False

    if not process_location(curr_file_name.location, curr_file_info.fileInfo.location_code):
        sensor_location_test = False
        notes += "Check Location values: Expected: %s, Actual %s\n" % (curr_file_name.location,
                                                                       curr_file_info.fileInfo.location_code)

    if notes == "":
        notes = "No errors in file\n"

    output_array = [file_name_to_test+"_"+curr_file_name.location, str(file_name_test), str(frequency_test),
                    str(page_count_test), str(sensor_location_test), notes]

    summary_df.loc[len(summary_df)] = output_array
    print(output_array)

summary_df.duplicated(subset=["Subject ID"], keep='last')

remove(destination+"Summary.csv")

summary_df.to_csv(destination+"Summary.csv")
