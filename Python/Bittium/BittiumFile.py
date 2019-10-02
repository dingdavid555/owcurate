

import os
import shutil
import datetime
import fpdf
import matplotlib.pyplot as plt
from matplotlib import style
import numpy as np
import pyedflib
import pandas as pd


class BittiumFile:
    ''' Class for interacting with Bittium .EDF data files.

    Attributes
    ----------
    file_path : str
        the path to the Bittium .edf file
    num_signals : int
        the number of different signal paths

    '''

    def __init__(self, file_path):
        ''' Parameters
        ----------
        file_path : str
            path to the Bittium .EDF file
        '''

        self.file_path = file_path
        self.num_signals = None
        self.signal_frequencies = None


