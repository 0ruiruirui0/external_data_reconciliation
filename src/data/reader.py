# data/reader.py

import pandas as pd

def read_text_file(file_path):
    """读取文本文件的内容并返回字符串"""
    try:
        with open(file_path, 'r') as file:
            content = file.read()
            return content
    except FileNotFoundError:
        return "文件未找到"
    except Exception as e:
        return f"发生错误: {e}"

def read_csv_file(file_path, delimiter=','):
    """读取CSV文件的内容并返回列表类型的数据"""
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
            data = [line.strip().split(delimiter) for line in lines]
            return data
    except FileNotFoundError:
        return "文件未找到"
    except Exception as e:
        return f"发生错误: {e}"


def read_sas_file(file_path,dataset_name):
    """读取SAS文件的内容并返回pandas数据框类型的数据"""
    data_frame = pd.read_sas(f"{file_path}{dataset_name}.sas7bdat")
    return data_frame

