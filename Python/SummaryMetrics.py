# David Ding
# September 11th 2019

# ======================= IMPORTS AND INITIALIZATIONS ======================
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math
from statistics import mean
from matplotlib import style
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
style.use("ggplot")


# ============================== DEFINITIONS ==============================
def avg_temp(dataframe, numofsamples):
    temperatures = []
    for chunk in np.array_split(dataframe, numofsamples):
        temperatures.append((chunk['Page Time'].iloc[0], mean(chunk['Temperature'])))
    return temperatures


def percent_clipping(dataframe, pergroup):
    # find how many points within a specified window the accelerometer spikes above 7.5 or below -7.5

    # Variable initialization and declaration
    clipped_x = 0
    clipped_y = 0
    clipped_z = 0
    x_val = 0
    y_val = 0
    z_val = 0
    clippings = []

    groups = dataframe.groupby(np.arange(len(dataframe.index))/pergroup)
    for (frameno, frame) in groups:
        # Reset values
        clipped_x = 0
        clipped_y = 0
        clipped_z = 0
        num_of_samples = 0
        # for index, row in frame.iterrows():
        num_of_samples += 1
        x_val = frame["X-val"]
        y_val = frame["Y-val"]
        z_val = frame["Z-val"]

        if abs(x_val) > 2:
            clipped_x += 1
        if abs(y_val) > 2:
            clipped_y += 1
        if abs(z_val) > 2:
            clipped_z += 1

        clippings.append([clipped_x/num_of_samples * 100,
                          clipped_y/num_of_samples * 100,
                          clipped_z/num_of_samples * 100])

    return clippings

# def accelerometry_stats():
    # finding mean

    # finding STD

    # finding IQR

    # finding Max/Min

# def worn():
    # not sure how to tackle this one yet...


acc_df = pd.read_csv("O:\\Data\\OND07\\Raw data\\GENEActiv\\Output\\OND07_WTL_3001_01_GA_LAnkle.csv",
                     nrows=10000,
                     names=["Index", "Time", "X-val", "Y-val", "Z-val"],
                     index_col=['Index'])

clipping_percentages = percent_clipping(acc_df, 900)
df = pd.DataFrame(data=clipping_percentages, columns=["X-clipping percent", "Y-clipping percent", "Z-clipping percent"])

df = df[(df['X-clipping percent'] > 0.0) | (df['Y-clipping percent'] > 0.0) | (df['Z-clipping percent'] > 0.0)]

print(df.head())
