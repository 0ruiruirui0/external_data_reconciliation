# -- coding: utf-8 --
__author__ = "ruijing.li"
__version__ = "0.1.0"

import logging
import pandas as pd
from datetime import datetime
from utils.config_utils import ISSUE_TYPE, ACTION_NEEDED
from utils.common import sort_data


def get_current_tracker(filename, *args) -> pd.DataFrame:
    # 创建一个空的数据框用于存储筛选过的数据
    data = pd.DataFrame()
    # 遍历每个数据框
    for df in [*args]:
        # 首次遍历时，定义需要保留的列
        columns_to_keep = ["SUBJID", "Subject", "VISIT", "InstanceName", "FolderSeq", "LBCAT", "cat", "var2",
                           "Issue_type", "Message",
                           "Var", "EDC", "External"]
        filtered_df = df.loc[(df["Message"] != "") & (pd.notnull(df["Message"])), columns_to_keep]
        data = pd.concat([data, filtered_df])

    # # 生成一列新的数据，作为index
    # data["index"] = data["SUBJID"] + data["Subject"] + data["VISIT"] + \
    #                          data["InstanceName"] + data["FolderSeq"].astype(str)

    data["Protocol Number"] = 'CPL-01-302'
    data["Vendor Name"] = 'LabConnect'
    data["Vendor Date"] = filename[:9] if filename is not None else ""

    data["Subject Number"] = data.apply(
        lambda x: x["SUBJID"] if not pd.isnull(x["SUBJID"]) else x["Subject"], axis=1)
    data["Site Number"] = data["Subject Number"].apply(
        lambda x: str(x).split("-")[0] if x is not None else None)
    data["Visit"] = data.apply(
        lambda x: x["VISIT"] if not pd.isnull(x["VISIT"]) else x["InstanceName"], axis=1)
    data["Test Name"] = data.apply(
        lambda x: x["LBCAT"] if not pd.isnull(x["LBCAT"]) else x["cat"], axis=1)

    # 将filtered_data全部转化成字符型

    data = data.apply(lambda x: x.astype(str))

    # 如果Var列中有多个变量，将其拆分成多行
    data["Var"] = data["Var"].apply(lambda x: x.split(";") if x is not None else None)
    data = data.explode("Var")
    data["Var"] = data["Var"].apply(lambda x: x.strip())

    data["Message"] = data["Message"].apply(lambda x: x.split(";") if x is not None else None)
    data["EDC"] = data["EDC"].apply(lambda x: x.split(";") if x is not None else None)
    data["External"] = data["External"].apply(lambda x: x.split(";") if x is not None else None)
    # Seq = 将Var以“.”进行分列，取第一个元素
    data["Seq"] = data["Var"].apply(lambda x: x.split(".")[0] if len(x.split(".")) > 1 else "0")
    data["Var"] = data["Var"].apply(lambda x: x.split(".")[1] if len(x.split(".")) > 1 else None)

    # Message1 = 如果seq为空，message取第一个元素，如果seq不为空，根据seq的结果转成整数后-1，取message中的第n个元素
    data["Message1"] = data.apply(
        lambda x: x["Message"][0] if x["Seq"] == "0" else x["Message"][int(x["Seq"]) - 1], axis=1)

    data["Message1"] = data["Message1"].apply(lambda x: '{0}:{1}'.format(datetime.now().strftime("%Y-%m-%d"),
                                                                         x.strip()))

    data["The Record of Database"] = data.apply(
        lambda x: x["EDC"][0] if x["Seq"] == "0" else x["EDC"][int(x["Seq"]) - 1], axis=1)

    data["The Record of Database"] = data["The Record of Database"].apply(lambda x: x.strip())

    data["The Record of Central Laboratory"] = data.apply(
        lambda x: x["External"][0] if x["Seq"] == "0" else x["External"][int(x["Seq"]) - 1], axis=1)

    data["The Record of Central Laboratory"] = data["The Record of Central Laboratory"].apply(lambda x: x.strip())

    # 将ISSUE_TYPE, ACTION_NEEDED结合成字典
    issue_type_dict = dict(zip(ISSUE_TYPE, ACTION_NEEDED))
    data["Action Needed"] = data["Issue_type"].apply(lambda x: issue_type_dict.get(x, "Null"))

    # 重命名列名
    data = data.rename(columns={"Issue_type": "Issue Type",
                                "Message1": "Data Manager Check Personnel and Date (DD-MMM-DD): comments",
                                "Var": "Variable name"})

    # 去除nan，None，Null
    data = data.fillna("").replace({"None": "", "Null": "", "nan": ""})

    # 生成数据编号
    # data["Issues Number"] = range(1, len(data) + 1)
    data["Central Lab Responder and Date (DD-MMM-DD): comments"] = ""

    columns = ["Protocol Number", "Vendor Name", "Vendor Date", "Site Number", "Subject Number", "Visit",
               "Test Name", "Variable name", "The Record of Database", "The Record of Central Laboratory",
               "Data Manager Check Personnel and Date (DD-MMM-DD): comments",
               "Central Lab Responder and Date (DD-MMM-DD): comments",
               "Issue Type", "Action Needed"]

    columns2 = [item.lower() for item in columns]

    rename_dict = dict(zip(columns, columns2))

    # 重新排序列
    data = data[columns]

    data = data.drop_duplicates(keep='first')
    data = data.sort_values(by=["Site Number", "Subject Number", "Visit", "Test Name", "Variable name"])
    data = data.rename(columns=rename_dict)
    data["solution"] = ""
    data["status"] = ""
    data["resolution date (dd-mmm-yyyy)"] = ""

    print(data.columns)

    return data

