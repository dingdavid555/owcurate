from Python.GENEActiv.nonwear import *

output_path = "C:\\Users\\y259ding\\Desktop\\presfiles\\Data\\"
input_path = "C:\\Users\\y259ding\\Desktop\\presfiles\\"


files = [f for f in listdir(input_path) if isfile(join(input_path, f))]

for f in files:
    print("Reading file %s" % f)
    Bin_file = ReadGENEActivBin(input_path + f)

    print("Parsing Hex")
    Bin_file.parse_hex()
    x_channel = np.array(Bin_file.x_channel)
    y_channel = np.array(Bin_file.y_channel)
    z_channel = np.array(Bin_file.z_channel)
    temps = np.array(Bin_file.temperatures)

    print("Outputting Files")
    x_channel.tofile("%s%i_%s_x-channel.bin" % (output_path, Bin_file.fileInfo.subject_code,
                                                Bin_file.fileInfo.location_code))
    y_channel.tofile("%s%i_%s_y-channel.bin" % (output_path, Bin_file.fileInfo.subject_code,
                                                Bin_file.fileInfo.location_code))
    z_channel.tofile("%s%i_%s_z-channel.bin" % (output_path, Bin_file.fileInfo.subject_code,
                                                Bin_file.fileInfo.location_code))
    temps.tofile("%s%i_%s_temps.bin" % (output_path, Bin_file.fileInfo.subject_code,
                                                Bin_file.fileInfo.location_code))

    with open(output_path+"Starts.txt", "a") as out:
        out.write("%s, %s\n" % (f, Bin_file.fileInfo.start_time.strftime("%m/%d/%Y %H:%M:%S%f")))

