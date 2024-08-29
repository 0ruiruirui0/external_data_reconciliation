# -- coding: utf-8 --
__author__ = "ruijing.li"
__version__ = "0.1.0"

import pandas as pd
import numpy as np

# def read_sas_file(file_path, dataset_name):
#     """读取SAS文件的内容并返回pandas数据框类型的数据"""
#     data = pd.read_sas(f"{file_path}{dataset_name}.sas7bdat", encoding='utf-8')
#     data = data.apply(lambda x: x.map(lambda y: y.strip() if isinstance(y, str) else y) if x.dtype == "object" else x)
#
#     def process_element(element):
#         if isinstance(element, str):
#             element = element.strip()
#         return element
#
#     # Apply the function to each element in the DataFrame
#     data = data.applymap(process_element)
#
#     # Replace empty strings, NaT, and nan with "Null"
#     data = data.replace({"": "Null", pd.NaT: "Null", np.nan: "Null"})
#
#     return data


# 写一个读入excel转化为df的方法，需要在转化的时候去除单元格内字符串上的空格，并且用None替换空字符串

def read_excel(path, data, sheet_name=None):
    xls = pd.ExcelFile(f"{path}{data}.xlsx", engine='openpyxl')
    if len(xls.sheet_names) == 1:
        df = pd.read_excel(xls, sheet_name=xls.sheet_names[0])
    else:
        df = pd.read_excel(xls, sheet_name=sheet_name)
    df = df.apply(lambda x: x.map(lambda y: y.strip() if isinstance(y, str) else y) if x.dtype == "object" else x)
    df = df.where(pd.notnull(df), "Null")
    return df



def read_sas_file(file_path, dataset_name):
    """读取SAS文件的内容并返回pandas数据框类型的数据"""
    data = pd.read_sas(f"{file_path}{dataset_name}.sas7bdat", encoding='utf-8')
    data = data.apply(lambda x: x.map(lambda y: y.strip() if isinstance(y, str) else y) if x.dtype == "object" else x)

    return data
