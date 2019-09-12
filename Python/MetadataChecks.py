# DAVID DING
# SEPTEMBER 12TH 2019
# This program generates a summary csv for each folder based on various checks for file integrity
# WORK IN PROGRESS

# ======================================== IMPORTS =============================
from owcurate.Python.GENEActivReader import *
import numpy as np
import pandas as pd
from statistics import mean, variance, stdev
from os import listdir, mkdir
from os.path import isfile, join


# ======================================== Reading files in and generating main DB
path = input("Please enter the file path: ")
in_path = '\\Raw data\\GENEActiv\\'
origin = path + in_path
out_path = "\\Processed Data\\"
destination = path + out_path
REDCap_dir = "\\Raw data\\REDCap\\"

files_to_check = [f for f in listdir(origin) if (isfile(join(origin, f)) and (".bin" in f))]
curr_file_name = None
curr_file_info = None

REDCap_files = [f for f in listdir(REDCap_dir) if isfile(join(REDCap_dir, f))]
df_Baseline = pd.read_csv(REDCap_dir + REDCap_files[0])
df_Discharge = pd.read_csv(REDCap_dir + REDCap_files[0])



## for f in files_to_check:


