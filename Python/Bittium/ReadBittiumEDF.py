import pyedflib
from fpdf import FPDF
import matplotlib.pyplot as plt
from matplotlib import style
import matplotlib.dates as md
from os import listdir, remove
from os.path import isfile, join
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

class BittiumFileName:
    def __init__(self, file):
        self.arr = file.split("_")
        self.study = self.arr[0][-5:]
        self.site = self.arr[1]
        self.subject_code = int(self.arr[2])
        self.visitNum = int(self.arr[3])
        self.location = self.arr[len(self.arr)-1][:-4]


