# -- coding: utf-8 --
__author__ = "ruijing.li"
__version__ = "0.1.0"

import logging
import pandas as pd
from data.sas_data import get_preg
from data.external_data import load_external_data
from data.external_data import load_visit_mapping_rules
from utils.common import compute_flags_and_vars_preg


def external_data_reco_preg(data_path, external_path, output_path) -> pd.DataFrame:
    """
    This function is used to reconciliation of external data for the given data.
    """
    logging.info("Start external data reconciliation...")
    logging.info("Data path: {}".format(data_path))
    logging.info("Output path: {}".format(output_path))

    external = load_external_data(external_path)
    folder_mapping = load_visit_mapping_rules(external_path)

    # 处理外部数据,根据foldermapping，统一folder名称
    external_data = external.loc[external["LBCAT"].str.contains("Serum Pregnancy")][
        ["SUBJID", "LBREFID","LBCAT", "VISIT", "LBSTAT", "LBREASND", "LBSPEC", "LBORRES", "LBSTRESC", "LBDTC"]].drop_duplicates(
        keep='first')

    external_data["TPT"] = "Null"

    external_data["LBDTC_Date"] = external_data["LBDTC"].apply(
        lambda x: x.split("T")[0].strip() if x is not None else None)

    external_data["LBDTC_Time"] = external_data["LBDTC"].apply(
        lambda x: x.split("T")[1].strip() if x is not None else None)

    external_data['visit_trans'] = external_data[['VISIT', 'TPT']].apply(
        lambda x: folder_mapping.get((x.iloc[0], x.iloc[1]), ''), axis=1)

    external_data['yn_trans'] = external_data['LBSTAT'].apply(lambda x: "Yes" if x == "Null" else "No")

    sas = get_preg(data_path)
    #
    # Merge data
    data = pd.merge(external_data, sas, left_on=['SUBJID', 'visit_trans'],
                    right_on=['Subject',
                              'FolderName'],
                    how="outer")

    # # 反馈比较结果
    data = data.apply(compute_flags_and_vars_preg, axis=1)
    data = data.sort_values(by=["Subject", "FolderSeq"])
    # Save data

    #去除nan，None，Null
    data = data.fillna("")
    data = data.replace("None", "")
    data = data.replace("Null", "")

    return data
