# ================================================================================
# DAVID DING
# SEPTEMBER 25TH 2019
# THIS FILE CONTAINS METHODS FOR THE WEAR/NON-WEAR TIMES
# ================================================================================

# IMPORTS
from owcurate.Python.GENEActiv.nonwear import *

# ======================================== MAIN ========================================
# Runs through the Data Pipeline to process for non-wear time
# bin_file is the GENEActivBin Object that stores relevant information

register_matplotlib_converters()

output_dir = "O:\\Data\\ReMiNDD\\Processed Data\\GENEActiv\\Non-wear\\"
input_dir = "O:\Data\OND07\Raw data\GENEActiv\\"
files = [f for f in listdir(input_dir) if isfile(join(input_dir, f))]


try:
    with open(output_dir+"Summary.csv") as file:
        df = pd.read_csv(file, names=["Index", "SubjectID", "DeviceLocation", "StartTime", "EndTime"],
                         header=0, index_col=["Index"])
except IOError:
    with open(output_dir+"Summary.csv", 'w') as file:
        file.write("Index,SubjectID,DeviceLocation,StartTime,EndTime\n")
        df = pd.DataFrame(columns=["SubjectID", "Location", "StartTime", "EndTime"], index=["Index"])


for f in files:
    file = join(input_dir, f)

    print("Initializing and Parsing Hexadecimal for %s" % file)
    t0 = datetime.now()
    bin_file = ReadGENEActivBin(file)

    print("Done Initializing File Object, parsing Hexadecimal")
    t1 = datetime.now()
    bin_file.parse_hex()
    init_time = bin_file.fileInfo.start_time

    t0 = datetime.now()
    print("Generating Times")
    times = np.array([init_time + timedelta(microseconds=13333.3333333 * i) for i in range(len(bin_file.x_channel))])

    print("Calculating SVMs")
    svms = calculate_svms(bin_file.x_channel, bin_file.y_channel, bin_file.z_channel)

    print("Filtering SVMs")
    filtered = filter_svms(svms)

    print("Finding Gaps")
    start_arr, end_arr = find_gaps(times, filtered)

    print("Finding Standard Deviation of Gaps... this might take a while")
    filt_start, filt_end = collapse_gaps(start_arr, end_arr, times, svms, 4, 5)

    print("Conducting Temperature Checks")
    start, end = temp_check(filt_start, filt_end, bin_file.temperatures, times)

    # Percentage of non-wear

    t1 = datetime.now()

    print("Plotting...")
    fig, ax = plt.subplots(figsize=(10, 6))
    fig.autofmt_xdate()
    ax.set_title(file)
    ax.plot(times, bin_file.x_channel, "black", linewidth=0.3)

    for i in range(len(start)):
        ax.axvline(start[i], -10, 10, c="red")
        ax.axvline(end[i], -10, 10, c="green")

    plt.savefig(output_dir + f[:-4])

    total_len = timedelta()
    for j in range(len(start)):
        df.loc[j] = [start[j], end[j]]
        total_len += end[j] - start[j]

    total_time = timedelta(hours=bin_file.fileInfo.measurement_period)
    percent_non_wear = (total_len / total_time) * 100

    df.to_csv(output_dir + f[:-4] + ".csv")

