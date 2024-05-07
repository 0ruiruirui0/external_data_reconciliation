import pandas as pd
import os

def save_df_to_excel(df, out_path, file_name, sheet_name='Sheet1', index=False):
    """
    将DataFrame保存到Excel文件
    :param df: 要保存的DataFrame
    :param out_path: Excel文件的路径
    :param file_name: Excel文件的文件名
    :param sheet_name: 工作表的名称
    :param index: 是否包含行索引，默认为 False
    """

    try:
        file_path = "{0}\\{1}".format(out_path, file_name)
        writer = pd.ExcelWriter(file_path, engine='xlsxwriter', datetime_format="yyyy/mm/dd hh:mm:ss",
                                date_format="yyyy/mm/dd")
        df.to_excel(excel_writer=writer, sheet_name=sheet_name, index=index)
        print(f"DataFrame已成功保存到Excel文件: {file_path}")
    except Exception as e:
        print(f"保存Excel文件时出现错误: {e}")
