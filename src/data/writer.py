# -- coding: utf-8 --
__author__ = "ruijing.li"
__version__ = "0.1.0"

import pandas as pd
import pyreadstat
from openpyxl import Workbook
from openpyxl.comments import Comment
from openpyxl.styles import Font
from openpyxl.styles import PatternFill, Border, Side, Alignment
from openpyxl.utils import get_column_letter
from openpyxl.utils.dataframe import dataframe_to_rows


def save_df_to_excel(df, out_path, file_name, sheet_name, index=False):
    """
    将DataFrame保存到Excel文件
    :param df: 要保存的DataFrame
    :param out_path: Excel文件的路径
    :param file_name: Excel文件的文件名
    :param sheet_name: 工作表的名称
    :param index: 是否包含行索引，默认为 False
    """

    try:
        # 保存到Excel文件
        file_path = "{0}\\{1}".format(out_path, file_name)
        wb = Workbook()
        ws = wb.active
        ws.title = sheet_name

        # 将DataFrame数据写入工作表
        for r in dataframe_to_rows(df, index=index, header=True):
            ws.append(r)

        # 设置列宽为50
        for cell in ws[1]:
            ws.column_dimensions[cell.column_letter].width = 15

        # 设置自动换行
        for row in ws.iter_rows(min_row=2, max_row=ws.max_row, min_col=1, max_col=ws.max_column):
            for cell in row:
                cell.alignment = Alignment(wrap_text=True)

        # 添加筛选器
        ws.auto_filter.ref = ws.dimensions

        # 保存Excel文件
        wb.save(file_path)


        # with pd.ExcelWriter(file_path,
        #                     datetime_format="yyyy/mm/dd hh:mm:ss",
        #                     date_format="yyyy/mm/dd",
        #                     engine='openpyxl'
        #                     ) as writer:
        #     df.to_excel(excel_writer=writer, sheet_name=sheet_name, index=index)

        # for key, sheet in writer.sheets.items():
        #     set_worksheet_format(sheet)
        #     print(f"调整表格格式: {sheet}")

        print(f"DataFrame已成功保存到Excel文件: {file_path}")
    except Exception as e:
        print(f"保存Excel文件时出现错误: {e}")

def set_worksheet_format(ws):
    ws.row_dimensions[1].height = 50
    for col in ws.columns:
        index = list(ws.columns).index(col)
        letter = get_column_letter(index + 1)
        ws.column_dimensions[letter].width = 14
        ws[f"{letter}1"].alignment = Alignment(wrapText=True)
    ws.auto_filter.ref = ws.dimensions
