# -- coding: utf-8 --
__author__ = "ruijing.li"
__version__ = "0.1.0"

import pandas as pd
from datetime import datetime
from data.reader import read_sas_file
def parse_date(date_str):
    if pd.notnull(date_str):
        return datetime.strptime(date_str, "%d/%b/%Y")
    else:
        return None

def format_date(date_obj):
    if pd.notnull(date_obj):
        return date_obj.strftime("%Y-%m-%d")
    else:
        return None

def get_subject_info(sas_path) -> pd.DataFrame:
    dm_raw = read_sas_file(sas_path, "dm")
    ic_raw = read_sas_file(sas_path, "ic")

    dm = dm_raw[["Subject", "AGE", "SEX"]].drop_duplicates(keep='first')
    ic = ic_raw[["Subject", "ICDT"]].drop_duplicates(keep='first')
    ic["ICDT_Y"] = ic["ICDT"].apply(lambda x: x.split("/")[2] if x is not None else None)
    df = pd.merge(dm, ic, on="Subject", how="left")
    return df


def get_hcu(sas_path) -> pd.DataFrame:
    hcu_raw = read_sas_file(sas_path, "hcu")
    hem = hcu_raw[["Subject","FolderName", "FolderSeq","HEMYN", "HEMANRSN","HEMADT"]].rename(
        columns={"HEMYN": "YN", "HEMANRSN": "NRSN", "HEMADT": "DAT"})
    hem["cat"] = "HEMYN"
    hem["cat2"] = "HEMADT"
    che = hcu_raw[["Subject","FolderName", "FolderSeq","CHEMYN", "CHEMNRSN","CHEMDT"]].rename(
        columns={"CHEMYN": "YN", "CHEMNRSN": "NRSN", "CHEMDT": "DAT"})
    che["cat"] = "CHEMYN"
    che["cat2"] = "CHEMDT"
    ur = hcu_raw[["Subject","FolderName", "FolderSeq","URINYN", "URINRSN","URINDT"]].rename(
        columns={"URINYN": "YN", "URINRSN": "NRSN", "URINDT": "DAT"})
    ur["cat"] = "URINYN"
    ur["cat2"] = "URINDT"
    hcu = pd.concat([hem, che, ur], ignore_index=True)
    hcu["DAT_formatted"] = hcu["DAT"].apply(parse_date)
    hcu["DAT_formatted"] = hcu["DAT_formatted"].apply(format_date)
    return hcu
