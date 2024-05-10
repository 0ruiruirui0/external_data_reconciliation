# -- coding: utf-8 --
__author__ = "ruijing.li"
__version__ = "0.1.0"

import pandas as pd
from data.reader import read_excel

def load_external_data(external_path):
    external_data = read_excel(external_path, "external_data")
    return external_data
