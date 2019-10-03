# ================================================================================
# DAVID DING
# SEPTEMBER 25TH 2019
# THIS FILE CONTAINS METHODS FOR THE WEAR/NON-WEAR TIMES
# ================================================================================

# IMPORTS
from Python.GENEActiv.nonwear import *

# ======================================== MAIN ========================================
# Runs through the Data Pipeline to process for non-wear time
# bin_file is the GENEActivBin Object that stores relevant information

register_matplotlib_converters()

output_dir = "O:\\Data\\ReMiNDD\\Processed Data\\GENEActiv\\Non-wear\\"
input_dir = "O:\\Data\\ReMiNDD\\Raw data\\GENEActiv\\"
files = [f for f in listdir(input_dir) if isfile(join(input_dir, f))]


try:
    with open(output_dir+"Summary.csv") as out:
        df = pd.read_csv(out, names=["Index", "SubjectID", "DeviceLocation", "StartTime", "EndTime"],
                         header=0, index_col=["Index"])
except IOError:
    with open(output_dir+"Summary.csv", 'w') as out:
        out.write("Index,SubjectID,DeviceLocation,StartTime,EndTime\n")
        df = pd.DataFrame(columns=["SubjectID", "Location", "StartTime", "EndTime"], index=["Index"])


for f in files:
    file = join(input_dir, f)

    t0 = datetime.now()
    print("Initializing and Parsing Hexadecimal for %s" % file)
    bin_file = ReadGENEActivBin(file)

    t1 = datetime.now()
    print("Done Initializing File Object, took {} seconds.".format(round((t1-t0).seconds)))
    print("======================================================================")
    print("Parsing Hexadecimal")
    bin_file.parse_hex()
    init_time = bin_file.fileInfo.start_time

    t2 = datetime.now()
    print("Done Parsing Hexadecimal, tok {} seconds.".format(round((t2-t1).seconds)))
    print("======================================================================")
    print("Generating Times")
    times = np.array([init_time + timedelta(microseconds=13333.3333333 * i) for i in range(len(bin_file.x_channel))])

    t3 = datetime.now()
    print("Done Generating times, took {} seconds.".format(round((t3-t2).seconds)))
    print("======================================================================")
    print("Calculating SVMs")
    svms = calculate_svms(bin_file.x_channel, bin_file.y_channel, bin_file.z_channel)

    t4 = datetime.now()
    print("Done calculating SVMs, took {} seconds".format(round((t4-t3).seconds)))
    print("======================================================================")
    print("Filtering SVMs")
    filtered = filter_svms(svms)

    t5 = datetime.now()
    print("Done filtering SVMs, took {} seconds.".format(round((t5-t4).seconds)))
    print("======================================================================")
    print("Finding Gaps")
    start_arr, end_arr = find_gaps(times, filtered)

    t6 = datetime.now()
    print("Done Finding Gaps, took {} seconds.".format(round((t6-t5).seconds)))
    print("======================================================================")
    print("Filtering Gaps, this might take a while")
    filt_start, filt_end = collapse_gaps(start_arr, end_arr, times, svms, 4, 5)

    t7 = datetime.now()
    print("Done Filtering Gaps, took {} seconds.".format(round((t7-t6).seconds)))
    print("======================================================================")
    print("Conducting Temperature Checks")
    start, end = temp_check(filt_start, filt_end, bin_file.temperatures, times)

    t8 = datetime.now()
    print("Done Conducting Temperature Checks, took {} seconds.".format(round((t8-t7).seconds)))
    print("======================================================================")

    print("Plotting...")
    fig, ax = plt.subplots(figsize=(10, 6))
    fig.autofmt_xdate()
    ax.set_title(file)
    ax.plot(times, bin_file.x_channel, "black", linewidth=0.3)

    out = open(output_dir+"Summary.csv", 'a')
    total_len = timedelta()
    for i in range(len(start)):
        ax.axvline(start[i], -10, 10, c="red")
        ax.axvline(end[i], -10, 10, c="green")
        out.write("%i,%s,%s,%s,%s\n" %(len(df), bin_file.fileInfo.subject_code, bin_file.fileInfo.location_code,
                                     start[i].strftime("%m/%d/%Y %H:%M:%S%f"), end[i].strftime("%m/%d/%Y %H:%M:%S%f")))
        df.loc[len(df)] = [bin_file.fileInfo.subject_code, bin_file.fileInfo.location_code, start[i], end[i]]
        total_len += end[i]-start[i]

    plt.savefig(output_dir + f[:-4])

    total_time = timedelta(hours=bin_file.fileInfo.measurement_period)
    percent_non_wear = (total_len / total_time) * 100

    # df.to_csv(output_dir + f[:-4] + ".csv")

    bin_file.file_instance_2.close()
    bin_file.file.close()
    out.close()

