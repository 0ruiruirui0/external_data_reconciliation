# -- coding: utf-8 --
__author__ = "ruijing.li"
__version__ = "0.1.0"

import pandas as pd
from data.reader import read_sas_file


def get_subject_info(sas_path) -> pd.DataFrame:
    dm_raw = read_sas_file(sas_path, "dm")
    ic_raw = read_sas_file(sas_path, "ic")

    dm = dm_raw[["Subject", "AGE", "SEX"]].drop_duplicates(keep='first')
    ic = ic_raw[["Subject", "ICDT"]].drop_duplicates(keep='first')
    ic["ICDT_Y"] = ic["ICDT"].apply(lambda x: x.split("/")[2] if x is not None else None)
    df = pd.merge(dm, ic, on="Subject", how="left")

    return df
