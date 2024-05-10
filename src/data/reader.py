# -- coding: utf-8 --
__author__ = "ruijing.li"
__version__ = "0.1.0"

import pandas as pd

def read_sas_file(file_path,dataset_name):
    """读取SAS文件的内容并返回pandas数据框类型的数据"""
    data_frame = pd.read_sas(f"{file_path}{dataset_name}.sas7bdat", encoding='utf-8')
    return data_frame

def read_excel(path, data):
    df = pd.read_excel(f"{path}{data}.xlsx")
    return df
