# David Ding

from owcurate.Python.GENEActivReader import *
from fpdf import FPDF
import matplotlib.pyplot as plt
from matplotlib import style
import matplotlib.dates as md
from os import listdir, remove
from os.path import isfile, join
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

style.use("ggplot")

# ================================= DEFINITIONS AND OBJECTS


# ================================== CONSTANTS AND VARIABLE DECLARATION ==============================
path = input("Please enter working path: ")
RAW_DATA = "\\Raw data\\GENEActiv\\"
REDCAP_PATH = "\\Raw data\\REDCap\\"
OUTPUT_PATH = "\\Processed Data\\PDF Summary\\"
working_dir = path + RAW_DATA
files = [f for f in listdir(path+RAW_DATA) if (isfile(join(working_dir, f)) and (".bin" in f) and not ("SAMPLE" in f))]

# pdf.cell(200, 10, txt="Welcome to Python!", ln=1, align="C")
# pdf.output("simple_demo.pdf")

# ============================= INITIALIZE FOLDER-ORIENTED DATABASES:
redcap_dir = path+REDCAP_PATH
REDCap_files = [f for f in listdir(redcap_dir) if isfile(join(redcap_dir, f))]
df_baseline = pd.read_csv(redcap_dir+REDCap_files[0])
df_discharge = pd.read_csv(redcap_dir+REDCap_files[0])
df_summary = pd.DataFrame(columns=["Index",
                                   "Filename (str)",
                                   "Start Time (datetime)",
                                   "x-gain (int)", "x-offset (int)",
                                   "y-gain (int)", "y-offset (int)",
                                   "z-gain (int)", "z-offset (int)",
                                   "Volts (int)", "Lux (int)"])
folder_indexer = 0


# MAKE HEADER PAGE
for f in files:
    # Setup PDF Instance for output
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Courier", size=12)

    # Read the input for the current file
    curr_bin_file = ReadGENEActivBin(join(working_dir, f))
    curr_filename = GENEActivFileName(f)
    curr_subj_code = curr_filename.study+"_"+curr_filename.site+"_%i" % curr_filename.subject_code
    curr_baseline = df_baseline[df_baseline["subject_id"] == curr_subj_code]
    curr_discharge = df_discharge[df_discharge["subject_id"] == curr_subj_code]

    # GETTING INPUT VALUES
    df_summary.loc[len(df_summary) + 1] = [folder_indexer, curr_subj_code, curr_bin_file.fileInfo.start_time,
                                           curr_bin_file.fileInfo.x_gain, curr_bin_file.fileInfo.x_offset,
                                           curr_bin_file.fileInfo.y_gain, curr_bin_file.fileInfo.y_offset,
                                           curr_bin_file.fileInfo.z_gain, curr_bin_file.fileInfo.z_offset,
                                           curr_bin_file.fileInfo.volts, curr_bin_file.fileInfo.lux]

    df_accelerometer = pd.DataFrame()

    # OUTPUTTING HEADER
    output_string = "FILENAME INFORMATION================================== \n" \
                    "Subject ID:%s\n" \
                    "Trial Code:%s\n" \
                    "Visit Number:%i\n" \
                    "Site ID:%s\n" \
                    "Location of device:%s\n\n" \
                    "BINARY FILE INFORMATION================================== \n" \
                    "Subject ID:%i\n" \
                    "Location of device:%s\n" \
                    "Measurement Frequency:%i\n" \
                    "Measurement Period:%i\n" \
                    "Start Time:%s\n" \
                    "Extract Time:%s\n" \
                    "Number of Pages:%s\n\n" \
                    "REDCAP BASELINE INFORMATION================================== \n" \
                    "Subject ID:%s\n\n" \
                    "REDCAP DISCHARGE INFORMATION================================== \n" \
                    "Subject ID:%s\n\n" % (curr_filename.subject_code,
                                           curr_filename.study,
                                           curr_filename.visitNum,
                                           curr_filename.site,
                                           curr_filename.location,
                                           curr_bin_file.fileInfo.subject_code,
                                           curr_bin_file.fileInfo.location_code,
                                           curr_bin_file.fileInfo.measurement_frequency,
                                           curr_bin_file.fileInfo.measurement_period,
                                           curr_bin_file.fileInfo.start_time,
                                           curr_bin_file.fileInfo.extract_time,
                                           curr_bin_file.fileInfo.number_of_pages,
                                           curr_baseline["subject_id"].to_list(),
                                           curr_discharge["subject_id"].to_list())

    # WRITE HEADER PAGE
    pdf.multi_cell(400, 5, output_string, align='L')

    # PROCESS GRAPHICAL DATA
    # First, we need to populate the hexadecimal valued database
    ticker = 0
    sequence = 0
    #for i in range(len()):
    x_vals = []
    y_vals = []
    z_vals = []
    time_vals = []

    temp_vals = []
    temp_time_vals = []

    for j, k in curr_bin_file.df.iterrows():
        time = k["Page Time"]
        # print(datetime.strftime(time, "%H:%M:%S"))
        curr_chunk = process_curr(k["Hexadecimal Data"], "", k["Sequence Number"], time,
                                  (curr_bin_file.fileInfo.x_offset, curr_bin_file.fileInfo.y_offset, curr_bin_file.fileInfo.z_offset),
                                  (curr_bin_file.fileInfo.x_gain, curr_bin_file.fileInfo.y_gain, curr_bin_file.fileInfo.z_gain))

        # print(k["Temperature"])
        # Get Temperature information
        temp_vals.append(k["Temperature"])
        temp_time_vals.append(time)

        # Extract x, y, z accelerometer data every chunk
        for l in range(300):
            time_vals.append(curr_chunk[l][1])
            x_vals.append(curr_chunk[l][2])
            y_vals.append(curr_chunk[l][3])
            z_vals.append(curr_chunk[l][4])

        if ticker == 3600 or sequence == curr_bin_file.actual_page_count:
            # Make the graph first, then output the graph
            sequence += 1
            plt.rcParams["figure.figsize"] = (6, 8.5)
            plt.suptitle("%s" % curr_subj_code)

            # X-axis subplot
            plt.subplot(411)
            axes = plt.gca()
            axes.set_ylim([-9, 9])
            axes.xaxis.set_major_formatter(md.DateFormatter("%H:%M:%S"))
            axes.xaxis.set_major_locator(plt.MaxNLocator(6))
            plt.ylabel("X component")
            plt.plot_date(time_vals, x_vals, "b-")

            # Y-axis subplot
            plt.subplot(412)
            axes = plt.gca()
            axes.set_ylim([-9, 9])
            axes.xaxis.set_major_formatter(md.DateFormatter("%H:%M:%S"))
            axes.xaxis.set_major_locator(plt.MaxNLocator(6))
            plt.ylabel("Y component")
            plt.plot_date(time_vals, y_vals, "r-")

            # Z-axis subplot
            plt.subplot(413)
            axes = plt.gca()
            axes.set_ylim([-9, 9])
            axes.xaxis.set_major_formatter(md.DateFormatter("%H:%M:%S"))
            axes.xaxis.set_major_locator(plt.MaxNLocator(6))
            plt.ylabel("Z component")
            plt.plot_date(time_vals, z_vals, "g-")

            # Temperature subplot
            plt.subplot(414)
            axes = plt.gca()
            axes.xaxis.set_major_formatter(md.DateFormatter("%H:%M:%S"))
            axes.xaxis.set_major_locator(plt.MaxNLocator(6))
            plt.ylabel("Temperature")
            plt.plot(temp_time_vals, temp_vals)

            temp_name = "%s_%i.png" % (curr_subj_code, sequence)
            plt.savefig(temp_name)
            # plt.show()
            pdf.add_page()
            pdf.image(temp_name, x=1, y=1, type='png')

            plt.close()
            # Clear the data since we do not want a running total
            x_vals.clear()
            y_vals.clear()
            z_vals.clear()
            time_vals.clear()
            temp_vals.clear()
            temp_time_vals.clear()
            ticker = 0
            remove(temp_name)

        ticker += 1
        percentage = (k["Sequence Number"] / curr_bin_file.actual_page_count * 100)
        print("Analyzing... Current Progress: %.2f%%" % percentage)

    pdf.output(path + OUTPUT_PATH + f[:-4] + ".pdf")
    folder_indexer += 1




