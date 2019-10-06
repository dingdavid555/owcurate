files = [LA_file, LW_file, RA_file, RW_file]
j = 0
k= 0
out = open(output_dir+"Filtered.csv", 'a')
summ = open(output_dir+"Summary.csv", "a")
for f in files:
    bin_file = f
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
                                        start[i].strftime("%m/%d/%Y %H:%M:%S.%f"),
                                        end[i].strftime("%m/%d/%Y %H:%M:%S.%f")))
