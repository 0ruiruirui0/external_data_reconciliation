# -- coding: utf-8 --
__author__ = "ruijing.li"
__version__ = "0.1.0"

import pandas as pd
from datetime import datetime
from data.reader import read_sas_file
from utils.config_utils import SYSTEM_COLUMNS


def parse_date(date_str):
    if pd.notnull(date_str):
        return datetime.strptime(date_str, "%d/%b/%Y")
    else:
        return None


# 写一个把HH:mm转化为HH:mm：ss的函数
def parse_time(time_str):
    if pd.notnull(time_str):
        return datetime.strptime(time_str, "%H:%M")
    else:
        return None


def format_date(date_obj):
    if pd.notnull(date_obj):
        return date_obj.strftime("%Y-%m-%d")
    else:
        return None


# 写一个把时间转化为字符串的函数
def format_time(time_obj):
    if pd.notnull(time_obj):
        return time_obj.strftime("%H:%M:%S")
    else:
        return None


def get_subject_info(sas_path) -> pd.DataFrame:
    dm_raw = read_sas_file(sas_path, "dm")
    ic_raw = read_sas_file(sas_path, "ic")

    dm = dm_raw[[*SYSTEM_COLUMNS, *["AGE", "SEX"]]].drop_duplicates(keep='first')
    ic = ic_raw[["Subject","ICDT"]].drop_duplicates(keep='first')
    ic["ICDT_Y"] = ic["ICDT"].apply(lambda x: x.split("/")[2] if x is not None else None)
    df = pd.merge(dm, ic, on="Subject", how="left")
    return df


def get_hcu(sas_path) -> pd.DataFrame:
    hcu_raw = read_sas_file(sas_path, "hcu")
    hem = hcu_raw[[*SYSTEM_COLUMNS, *["HEMYN", "HEMANRSN", "HEMADT"]]].rename(
        columns={"HEMYN": "YN", "HEMANRSN": "NRSN", "HEMADT": "DAT"})
    hem["cat"] = "Hematology"
    hem["var1"] = "HEMYN"
    hem["var2"] = "HEMADT"
    che = hcu_raw[[*SYSTEM_COLUMNS, *["CHEMYN", "CHEMNRSN", "CHEMDT"]]].rename(
        columns={"CHEMYN": "YN", "CHEMNRSN": "NRSN", "CHEMDT": "DAT"})
    che["cat"] = "Chemistry"
    che["var1"] = "CHEMYN"
    che["var2"] = "CHEMDT"
    ur = hcu_raw[[*SYSTEM_COLUMNS, *["URINYN", "URINRSN", "URINDT"]]].rename(
        columns={"URINYN": "YN", "URINRSN": "NRSN", "URINDT": "DAT"})
    ur["cat"] = "Urinalysis"
    ur["var1"] = "URINYN"
    ur["var2"] = "URINDT"
    hcu = pd.concat([hem, che, ur], ignore_index=True)
    hcu["DAT_formatted"] = hcu["DAT"].apply(parse_date)
    hcu["DAT_formatted"] = hcu["DAT_formatted"].apply(format_date)
    return hcu


def get_pk(sas_path) -> pd.DataFrame:
    raw = read_sas_file(sas_path, "pk")
    pk = raw[[*SYSTEM_COLUMNS, *["PKYN", "PKNDREAS", "PKDAT", "PKTIM"]]].rename(
        columns={"PKYN": "YN", "PKNDREAS": "NRSN", "PKDAT": "DAT", "PKTIM": "TIM"})
    pk["TP"] = "Null"
    pk["cat"] = "PK Blood Sampling"
    pk["var1"] = "PKYN"
    pk["var2"] = "PKDAT"
    pk["var3"] = "PKTIM"

    raw1 = read_sas_file(sas_path, "pk1")
    pk1 = raw1[[*SYSTEM_COLUMNS, *["PK1TPT", "TMPTND", "PK1RESND", "PK1DAT", "PK1TIM"]]].rename(
        columns={"PK1TPT": "TP", "PK1RESND": "NRSN", "PK1DAT": "DAT", "PK1TIM": "TIM"})

    pk1["YN"] = pk1["TMPTND"].apply(lambda x: "Yes" if x == "0" else "No" if x == "1" else "Null" if pd.isnull(x)
    else x)
    pk1 = pk1.drop("TMPTND", axis=1)
    pk1["cat"] = "PK 1 Blood Sampling"
    pk1["var1"] = "TMPTND"
    pk1["var2"] = "PK1DAT"
    pk1["var3"] = "PK1TIM"

    raw2 = read_sas_file(sas_path, "pk2")
    pk2 = raw2[[*SYSTEM_COLUMNS, *["PK2TPT", "TMPTND", "PK2RESND", "PK2DAT", "PK2TIM"]]].rename(
        columns={"PK2TPT": "TP", "PK2RESND": "NRSN", "PK2DAT": "DAT", "PK2TIM": "TIM"})

    pk2["YN"] = pk2["TMPTND"].apply(lambda x: "Yes" if x == "0" else "No" if x == "1" else "Null" if pd.isnull(x)
    else x)
    pk2 = pk2.drop("TMPTND", axis=1)
    pk2["cat"] = "PK 2 Blood Sampling"
    pk2["var1"] = "TMPTND"
    pk2["var2"] = "PK2DAT"
    pk2["var3"] = "PK2TIM"

    sas = pd.concat([pk1, pk2, pk], ignore_index=True)
    sas["DAT_formatted"] = sas["DAT"].apply(parse_date)
    sas["DAT_formatted"] = sas["DAT_formatted"].apply(format_date)
    sas["TIM_formatted"] = sas["TIM"].apply(parse_time)
    sas["TIM_formatted"] = sas["TIM_formatted"].apply(format_time)
    return sas


def get_preg(sas_path) -> pd.DataFrame:
    raw = read_sas_file(sas_path, "preg")
    preg = raw[[*SYSTEM_COLUMNS, *["PRGYN", "PRGNRE", "PRGDT", "RPTEST", "PRGRES"]]].rename(
        columns={"PRGYN": "YN", "PRGNRE": "NRSN", "PRGDT": "DAT", "RPTEST": "TERM", "PRGRES": "RESULT"})
    preg.loc[:, "DAT_formatted"] = preg["DAT"].apply(parse_date)
    preg["DAT_formatted"] = preg["DAT_formatted"].apply(format_date)
    preg["cat"] = "Pregnancy Test"
    preg["var1"] = "PRGYN"
    preg["var2"] = "PRGDT"
    preg["var3"] = "RPTEST"
    preg["var4"] = "PRGRES"
    return preg


def get_ser(sas_path) -> pd.DataFrame:
    raw = read_sas_file(sas_path, "ser")
    df = raw[[*SYSTEM_COLUMNS, *["SERYN", "SERREASN", "SERDAT", "SERTEST", "SERRES"]]].rename(
        columns={"SERYN": "YN", "SERREASN": "NRSN", "SERDAT": "DAT", "SERTEST": "TERM", "SERRES": "RESULT"})
    df.loc[:, "DAT_formatted"] = df["DAT"].apply(parse_date)
    df["DAT_formatted"] = df["DAT_formatted"].apply(format_date)
    df["cat"] = "Serology"
    df["var1"] = "SERYN"
    df["var2"] = "SERDAT"
    df["var3"] = "SERRES"
    return df
