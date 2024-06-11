# -- coding: utf-8 --
__author__ = "ruijing.li"
__version__ = "0.1.0"

import logging
import pandas as pd
from data.sas_data import get_subject_info
from data.external_data import load_external_data
from utils.common import compute_flags_and_vars_dm


def external_data_reco_dm(data_path, external_path, output_path) -> pd.DataFrame:
    """
    This function is used to reconciliation of external data for the given data.
    """
    logging.info("Start external data reconciliation...")
    logging.info("Data path: {}".format(data_path))
    logging.info("Output path: {}".format(output_path))

    external_data = load_external_data(external_path)
    dm_external_data = external_data[["SUBJID", "LBREFID","LBCAT", "YOB", "SEX"]].drop_duplicates(keep='first')
    # 外部数据中的YOB原本是Float类型
    dm_external_data["YOB"] = dm_external_data["YOB"].apply(lambda x: int(x) if x is not None else None)
    dm_external_data["SUBJID"] = dm_external_data["SUBJID"].apply(lambda x: x.strip())
    subject_info = get_subject_info(data_path)

    # Merge data
    data = pd.merge(dm_external_data, subject_info, left_on=['SUBJID'], right_on=['Subject'], how="outer")

    data["YOB_trans"] = data.apply(
        lambda x: str(int(x["ICDT_Y"]) - x["YOB"]) if x["ICDT_Y"] is not None and x["YOB"] is not None
        else None,
        axis=1)
    remove_decimal_zeros = lambda x: x.rstrip('0').rstrip('.') if '.' in x else x
    data["YOB_trans"] = data["YOB_trans"].apply(lambda x: remove_decimal_zeros(x) if pd.notnull(x) else x)
    data["YOB_cal"] = (data["YOB_trans"].astype(float, errors='ignore') - 1).astype(str, errors='ignore').apply(
        lambda x:
        remove_decimal_zeros(x)
        if pd.notnull(x) else x)
    # TODO：转化为读取dictionary的写法
    data["SEX_trans"] = data.apply(lambda x: {"Male": "M", "Female": "F"}.get(x["SEX_y"], None), axis=1)
    # 反馈比较结果
    data = data.apply(compute_flags_and_vars_dm, axis=1)
    data = data.sort_values(by=["Subject"])

    data["cat"] = "DM"


    #去除nan，None，Null
    data = data.fillna("")
    data = data.replace("None", "")
    data = data.replace("Null", "")

    # Save data
    return data
