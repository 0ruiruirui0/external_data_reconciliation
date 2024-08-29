# -- coding: utf-8 --
__author__ = "ruijing.li"
__version__ = "0.1.0"

import time
import tkinter as tk
import logging
import os
import glob
import sys
import traceback
import pandas as pd
import datacompy
from functools import partial
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
from tkinter import Label
from src.data.writer import set_worksheet_format
from tests.config import *
from external_data_reco.dm import external_data_reco_dm
from external_data_reco.hcu import external_data_reco_hcu
from external_data_reco.pk import external_data_reco_pk
from external_data_reco.preg import external_data_reco_preg
from external_data_reco.ser import external_data_reco_ser
from external_data_reco.tracker import get_current_tracker
from utils.common import compare_data_common, sort_data
from external_data_reco.compare_tracker import compare_data_tracker_record

# 获取当前文件的绝对路径
current_file_path = os.path.abspath(__file__)
# 获取当前文件的父目录
src_path = os.path.dirname(current_file_path)
project_path = os.path.abspath(os.path.join(src_path, os.pardir))
# 将项目路径设置为运行路径
os.chdir(project_path)


def select_file(str_var):
    directory = filedialog.askdirectory()
    str_var.set(directory)


LARGE_FONT = ("Arial", 12)
LARGE_FONT_ENTRY = ("Arial", 10)

logger = logging.getLogger()
logger.setLevel(logging.WARNING)

# 设置屏幕打印的格式
sh = logging.StreamHandler()
# sh.setFormatter()
logger.addHandler(sh)

app = tk.Tk()
app.title("external_data_reco")
app.geometry("1060x200")

frame = tk.Frame(app, width=300, height=300)

str_outputflag = tk.StringVar(frame)
str_raw = tk.StringVar(frame)
str_old_file = tk.StringVar(frame)
str_new_file = tk.StringVar(frame)

entry_raw = tk.Entry(frame, textvariable=str_raw, width=100, font=LARGE_FONT_ENTRY)
entry_old_file = tk.Entry(frame, textvariable=str_old_file, width=100, font=LARGE_FONT_ENTRY)
entry_new_file = tk.Entry(frame, textvariable=str_new_file, width=100, font=LARGE_FONT_ENTRY)

tkk_outputflag = ttk.Combobox(frame)
tkk_outputflag['values'] = ["OldData->NewData", "批注", "NewDataOnly"]
tkk_outputflag['state'] = 'readonly'

bt_open_raw = tk.Button(frame,
                        text="请选择配置文件所在的文件夹路径：",
                        command=partial(select_file, str_raw),
                        font=LARGE_FONT,
                        width=28,
                        relief="raised")

bt_open_old = tk.Button(frame,
                        text="选择上一次的源数据：",
                        command=partial(select_file, str_old_file),
                        font=LARGE_FONT,
                        width=28,
                        relief="raised")

bt_open_new = tk.Button(frame,
                        text="选择本次的源数据：",
                        command=partial(select_file, str_new_file),
                        font=LARGE_FONT,
                        width=28,
                        relief="raised")


# TODO:
# 增加config文件读取
# from src.utils.config_utils import load_config
# config = load_config()
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def data_handler():
    path_input_old = '{0}\\'.format(str_old_file.get())
    path_input_new = '{0}\\'.format(str_new_file.get())
    path_input_project = '{0}\\'.format(str_raw.get())
    path_output = '{0}\\Output\\{1}\\'.format(str_raw.get(), datetime.now().strftime("%Y-%m-%d"))

    raw_path_old = '{0}\\SAS\\'.format(path_input_old)
    raw_path_new = '{0}\\SAS\\'.format(path_input_new)

    def find_first_csv(path):
        os.chdir(path)
        csv_files = glob.glob('*.csv')
        if csv_files:
            return csv_files[0]
        else:
            return "No csv files found in the provided path."

    def find_first_xlsx(path):
        os.chdir(path)
        files = glob.glob('*.xlsx')
        if files:
            return files[0]
        else:
            return "No xlsx files found in the provided path."

    print(find_first_csv(path_input_old))
    print(find_first_csv(path_input_new))
    print(find_first_xlsx(path_input_old))

    # raw_path = '{0}\\test_data\\project1\\Old\\SAS\\'.format(project_path)
    # external_path = '{0}\\test_data\\project1\\Old\\'.format(project_path)
    # output_path = '{0}\\test_data\\project1\\output'.format(project_path)
    file_name_old = find_first_csv(path_input_old)
    file_name_new = find_first_csv(path_input_new)

    path_old_tracker = find_first_xlsx(path_input_old)

    old_tracker = pd.read_excel(path_old_tracker, sheet_name="Tracker", dtype=str)
    print(old_tracker.columns)

    if not os.path.exists(path_output):
        os.makedirs(path_output)

    def load_external_data(file_path, file_name):
        path = "{}{}".format(file_path, file_name)
        df = pd.read_csv(path, dtype=str, encoding="utf-8")
        df = df.fillna("")
        return df

    # 测试代码运行时间
    start_time = time.time()

    external_data_old = load_external_data(path_input_old, file_name_old)
    external_data_new = load_external_data(path_input_new, file_name_new)

    end_time = time.time()
    execution_time = end_time - start_time

    print(f"Execution time of csv: {execution_time} seconds")

    print("********** Finish loading External Data! **********")

    start_time = time.time()
    dm_old = external_data_reco_dm(raw_path_old, external_data_old)
    dm_new = external_data_reco_dm(raw_path_new, external_data_new)
    key_list_dm = ["SUBJID", "Subject", "LBREFID"]
    dm = compare_data_common(dm_old, dm_new, key_list_dm)
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Execution time of dm: {execution_time} seconds")
    print("********** Finish Processing DM! **********")

    start_time = time.time()
    hcu_old = external_data_reco_hcu(raw_path_old, external_data_old, path_input_project)
    hcu_new = external_data_reco_hcu(raw_path_new, external_data_new, path_input_project)
    print(f"hcu_columns: {hcu_new.columns}")
    key_list_huc = ["SUBJID", "Subject", "LBREFID", "VISIT", "InstanceName", "LBCAT", "LBTEST", 'cat']
    hcu = compare_data_common(hcu_old, hcu_new, key_list_huc)
    hcu = hcu.apply(lambda x: x.replace('Null', ''), axis=1).apply(lambda x: x.replace('nan', ''), axis=1)
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Execution time of hcu: {execution_time} seconds")
    print("********** Finish Processing HCU! **********")

    start_time = time.time()
    pk_old = external_data_reco_pk(raw_path_old, external_data_old, path_input_project)
    pk_new = external_data_reco_pk(raw_path_new, external_data_new, path_input_project)
    print(f"pk_columns: {pk_new.columns}")
    key_list_pk = ["SUBJID", "Subject", "LBREFID", "VISIT", "InstanceName", "LBCAT", "cat", "LBTPT", "TP"]
    pk = compare_data_common(pk_old, pk_new, key_list_pk)
    pk = pk.apply(lambda x: x.replace('Null', ''), axis=1)
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Execution time of PK: {execution_time} seconds")
    print("********** Finish Processing PK! **********")

    start_time = time.time()
    preg_old = external_data_reco_preg(raw_path_old, external_data_old, path_input_project)
    preg_new = external_data_reco_preg(raw_path_new, external_data_new, path_input_project)
    key_list_preg = ["SUBJID", "Subject", "VISIT", "InstanceName", "TERM", "LBREFID"]
    preg = compare_data_common(preg_old, preg_new, key_list_preg)
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Execution time of PREG: {execution_time} seconds")
    print("********** Finish Processing PREG! **********")

    start_time = time.time()
    ser_old = external_data_reco_ser(raw_path_old, external_data_old, path_input_project)
    ser_new = external_data_reco_ser(raw_path_new, external_data_new, path_input_project)
    print(f"ser_columns: {ser_new.columns}")
    key_list_ser = ["SUBJID", "Subject", "VISIT", "InstanceName", "TERM", "LBREFID"]
    ser = compare_data_common(ser_old, ser_new, key_list_ser)
    ser = ser.apply(lambda x: x.replace('Null', ''), axis=1)
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Execution time of SER: {execution_time} seconds")
    print("********** Finish Processing SER! **********")

    start_time = time.time()

    tracker_old = old_tracker
    tracker_new = get_current_tracker(file_name_new, dm_new, hcu_new, pk_new, preg_new, ser_new)

    # 情况1：整行记录缺失
    # 新旧中都missing record
    old_data_1 = tracker_old[tracker_old['variable name'].isnull() | (tracker_old['variable name'] == '')]
    print(f"旧数据中整行缺失的数据：{len(old_data_1)}")
    new_data_1 = tracker_new[tracker_new['variable name'].isnull() | (tracker_new['variable name'] == '')]
    print(f"新数据中整行缺失的数据：{len(new_data_1)}")
    key_list_tracker_record = ["site number", "subject number", "visit", "test name"]
    not_compare_record = ["protocol number", "vendor name", "vendor date", "variable name"]
    tracker_record = compare_data_tracker_record(old_data_1, new_data_1, key_list_tracker_record, not_compare_record)

    # 情况2：变量数据变更
    old_data_2 = tracker_old[(tracker_old['variable name'].notna()) & (tracker_old['variable name'] != '')]
    print(f"旧数据中与外部数据不一致的数据：{len(old_data_2)}")
    new_data_2 = tracker_new[(tracker_new['variable name'].notna()) & (tracker_new['variable name'] != '')]
    print(f"新数据中与外部数据不一致的数据：{len(new_data_2)}")
    key_list_tracker_var = ["site number", "subject number", "visit", "test name", "variable name"]
    not_compare_var = ["protocol number", "vendor name", "vendor date"]
    tracker_var = compare_data_tracker_record(old_data_2, new_data_2, key_list_tracker_var, not_compare_var)

    tracker = pd.concat([tracker_record, tracker_var], ignore_index=True)

    # end
    tracker = sort_data(tracker, key_list_tracker_var)
    tracker["Issues Number"] = range(1, len(tracker) + 1)
    col_name = tracker.columns.tolist()
    col_name.insert(0, col_name.pop(col_name.index('Issues Number')))
    tracker = tracker.reindex(columns=col_name)
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Execution time of TRACKER: {execution_time} seconds")
    print("********** Finish Processing tracker! **********")

    dm_list = ["SUBJID", "LBREFID", "YOB", "SEX_x", "Subject", "AGE", "SEX_y", "Issue_type", "Message", "Var"]
    dm = dm[[item.lower() for item in dm_list] + ["Flag"]]

    hcu_list = ["SUBJID", "LBREFID", "VISIT", "LBTEST", "LBCAT", "LBSTAT", "LBREASND", "LBDTC_Date", "LBDTC_Time", "Subject",
         "InstanceName", "FolderName", "YN", "NRSN", "DAT", "Issue_type", "Message", "Var"]
    hcu = hcu[[item.lower() for item in hcu_list] + ["Flag"]]

    pk_list = ["SUBJID", "LBREFID", "VISIT", "LBCAT", "LBTPT", "LBSTAT", "LBREASND", "LBDTC_Date", "LBDTC_Time", "Subject",
         "InstanceName", "FolderName", "TP", "YN", "NRSN", "DAT", "TIM", "Issue_type", "Message", "Var"]
    pk = pk[[item.lower() for item in pk_list] + ["Flag"]]

    preg_list = ["SUBJID", "LBREFID", "VISIT", "LBSTAT", "LBREASND", "LBSPEC", "LBSTRESC", "LBDTC_Date", "LBDTC_Time",
                 "Subject", "InstanceName", "FolderName", "YN", "NRSN", "DAT", "TERM", "RESULT", "Issue_type",
                 "Message", "Var"]
    preg = preg[[item.lower() for item in preg_list] + ["Flag"]]

    ser_list = ["SUBJID", "LBREFID", "VISIT", "LBSTAT", "LBREASND", "LBSTRESC", "LBDTC_Date", "LBDTC_Time", "Subject",
     "InstanceName", "FolderName", "YN", "NRSN", "DAT", "TERM", "RESULT", "Issue_type", "Message", "Var"]
    ser = ser[[item.lower() for item in ser_list] + ["Flag"]]

    file = f"Output_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.xlsx"

    with pd.ExcelWriter("{0}\\{1}".format(path_output, file), engine='openpyxl', datetime_format="yyyy/mm/dd hh:mm:ss",
                        date_format="yyyy/mm/dd") as writer:
        try:
            print("********** Start To Writer! **********")
            dm.to_excel(excel_writer=writer, sheet_name="DM", index=False)
            print("********** Finish write DM! **********")
            hcu.to_excel(excel_writer=writer, sheet_name="HCU", index=False)
            print("********** Finish write HCU! **********")
            pk.to_excel(excel_writer=writer, sheet_name="PK", index=False)
            print("********** Finish write PK! **********")
            preg.to_excel(excel_writer=writer, sheet_name="PREG", index=False)
            print("********** Finish write PREG! **********")
            ser.to_excel(excel_writer=writer, sheet_name="SER", index=False)
            print("********** Finish write SER! **********")
            tracker.to_excel(excel_writer=writer, sheet_name="Tracker", index=False)
            tracker_new.to_excel(excel_writer=writer, sheet_name="Tracker_current", index=False)
            tracker_old.to_excel(excel_writer=writer, sheet_name="Tracker_old", index=False)
            print("********** Finish write Tracker! **********")
            print("********** Done! **********")

        except Exception as e:
            "输出数据集失败，原因：{0}".format(e)

        for key, sheet in writer.sheets.items():
            set_worksheet_format(sheet)


bt_run = tk.Button(frame,
                   text="运行",
                   command=data_handler,
                   font=LARGE_FONT,
                   width=20,
                   relief="raised")

# layout
frame.grid(row=0, column=0, sticky="WESN")

# 源数据+目录路径
system_label = Label(frame, text="请选择对比数据输出方式", font=LARGE_FONT)
system_label.grid(row=1, column=0, padx=5, pady=2, sticky="WESN")
tkk_outputflag.grid(row=1, column=1, padx=2, pady=2, sticky="w")
bt_open_raw.grid(row=4, column=0, padx=5, pady=2, sticky="w")
bt_open_old.grid(row=2, column=0, padx=5, pady=2, sticky="w")
bt_open_new.grid(row=3, column=0, padx=5, pady=2, sticky="w")

entry_raw.grid(row=4, column=1, padx=2, pady=2, sticky="w")
entry_new_file.grid(row=3, column=1, padx=2, pady=2, sticky="w")

bt_run.grid(row=7, column=1, padx=2, pady=20, sticky="w")

if __name__ == '__main__':
    app.mainloop()

print("********** Done! **********")
entry_old_file.grid(row=2, column=1, padx=2, pady=2, sticky="w")
