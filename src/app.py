# -- coding: utf-8 --
__author__ = "ruijing.li"
__version__ = "0.1.0"

import pandas as pd
import numpy as np
import os
import sys
import openpyxl
import logging
from src.data.writer import set_worksheet_format
from tests.config import *
from external_data_reco.dm import external_data_reco_dm
from external_data_reco.hcu import external_data_reco_hcu
from external_data_reco.pk import external_data_reco_pk
from external_data_reco.preg import external_data_reco_preg
from external_data_reco.ser import external_data_reco_ser
from external_data_reco.tracker import get_tracker

# 获取当前文件的绝对路径
current_file_path = os.path.abspath(__file__)
# 获取当前文件的父目录
src_path = os.path.dirname(current_file_path)
project_path = os.path.abspath(os.path.join(src_path, os.pardir))
# 将项目路径设置为运行路径
os.chdir(project_path)

# TODO:
# 增加config文件读取
# from src.utils.config_utils import load_config
# config = load_config()
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

if __name__ == '__main__':
    raw_path = '{0}\\test_data\\project1\\SAS\\'.format(project_path)
    external_path = '{0}\\test_data\\project1\\'.format(project_path)
    output_path = '{0}\\test_data\\project1\\output'.format(project_path)

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    dm = external_data_reco_dm(raw_path, external_path, output_path)
    dm = dm.apply(lambda x: x.replace('Null', ''), axis=1)
    hcu = external_data_reco_hcu(raw_path, external_path, output_path)
    hcu = hcu.apply(lambda x: x.replace('Null', ''), axis=1)
    pk = external_data_reco_pk(raw_path, external_path, output_path)
    pk = pk.apply(lambda x: x.replace('Null', ''), axis=1)
    preg = external_data_reco_preg(raw_path, external_path, output_path)
    preg = preg.apply(lambda x: x.replace('Null', ''), axis=1)
    ser = external_data_reco_ser(raw_path, external_path, output_path)
    ser = ser.apply(lambda x: x.replace('Null', ''), axis=1)

    tracker = get_tracker(hcu, pk, preg, ser)

    dm = dm[["SUBJID", "LBREFID", "YOB", "SEX_x", "Subject", "AGE", "SEX_y", "Issue_type", "Message", "Var"]]
    hcu = hcu[
        ["SUBJID", "LBREFID", "VISIT", "LBTEST", "LBCAT", "LBSTAT", "LBREASND", "LBDTC_Date", "LBDTC_Time", "Subject",
         "InstanceName", "FolderName", "YN", "NRSN", "DAT", "Issue_type", "Message", "Var"]]
    pk = pk[
        ["SUBJID", "LBREFID", "VISIT", "LBCAT", "LBTPT", "LBSTAT", "LBREASND", "LBDTC_Date", "LBDTC_Time", "Subject",
         "InstanceName", "FolderName", "TP", "YN", "NRSN", "DAT", "TIM", "Issue_type", "Message", "Var"]]
    preg = preg[["SUBJID", "LBREFID", "VISIT", "LBSTAT", "LBREASND", "LBSPEC", "LBSTRESC", "LBDTC_Date", "LBDTC_Time",
                 "Subject", "InstanceName", "FolderName", "YN", "NRSN", "DAT", "TERM", "RESULT", "Issue_type",
                 "Message", "Var"]]
    ser = ser[["SUBJID", "LBREFID", "VISIT", "LBSTAT", "LBREASND", "LBSTRESC", "LBDTC_Date", "LBDTC_Time", "Subject",
               "InstanceName", "FolderName", "YN", "NRSN", "DAT", "TERM", "RESULT", "Issue_type", "Message", "Var"]]

    file = f"Output_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.xlsx"

    with pd.ExcelWriter("{0}\\{1}".format(output_path, file), engine='openpyxl', datetime_format="yyyy/mm/dd hh:mm:ss",
                        date_format="yyyy/mm/dd") as writer:
        try:
            dm.to_excel(excel_writer=writer, sheet_name="DM", index=False)
            hcu.to_excel(excel_writer=writer, sheet_name="HCU", index=False)
            pk.to_excel(excel_writer=writer, sheet_name="PK", index=False)
            preg.to_excel(excel_writer=writer, sheet_name="PREG", index=False)
            ser.to_excel(excel_writer=writer, sheet_name="SER", index=False)
            tracker.to_excel(excel_writer=writer, sheet_name="Tracker", index=False)
        except Exception as e:
            error_msg = "输出数据集失败，原因：{0}".format(e)

        for key, sheet in writer.sheets.items():
            set_worksheet_format(sheet)

    print("********** Done! **********")
