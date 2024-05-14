# -- coding: utf-8 --
__author__ = "ruijing.li"
__version__ = "0.1.0"

import os
import logging
import pandas as pd
from datetime import datetime
from data.reader import read_excel
from data.sas_data import get_hcu
from data.external_data import load_external_data
from data.external_data import load_visit_mapping_rules
from data.external_data import load_category_mapping
from utils.common import compute_flags_and_vars_lab


def external_data_reco_hcu(data_path, external_path, output_path) -> pd.DataFrame:
    """
    This function is used to reconciliation of external data for the given data.
    """
    logging.info("Start external data reconciliation...")
    logging.info("Data path: {}".format(data_path))
    logging.info("Output path: {}".format(output_path))

    external_data = load_external_data(external_path)
    folder_mapping = load_visit_mapping_rules(external_path)
    category_mapping = load_category_mapping(external_path)

    # 处理外部数据,根据foldermapping，统一folder名称
    hcu_external_data = external_data.loc[
        (external_data.LBCAT == "Chemistry") | (external_data.LBCAT == "Hematology") | (external_data.LBCAT ==
                                                                                        "Urinalysis")][
        ["SUBJID", "LBREFID", "VISIT", "LBTPT", "LBTEST", "LBCAT", "LBSTAT", "LBREASND", "LBDTC"]].drop_duplicates(
        keep='first')

    hcu_external_data["LBDTC_Date"] = hcu_external_data["LBDTC"].apply(
        lambda x: x.split("T")[0].strip() if x is not None else None)

    hcu_external_data["LBDTC_Time"] = hcu_external_data["LBDTC"].apply(
        lambda x: x.split("T")[1].strip() if x is not None else None)

    hcu_external_data['visit_trans'] = hcu_external_data[['VISIT', 'LBTPT']].apply(
        lambda x: folder_mapping.get((x.iloc[0],
                                      x.iloc[1]), ''), axis=1)


    hcu_external_data['cat_trans'] = hcu_external_data[['LBCAT']].apply(
        lambda x: category_mapping.get((x.iloc[0]), ''), axis=1)
    hcu_external_data['yn_trans'] = hcu_external_data['LBSTAT'].apply(lambda x: "Yes" if pd.isnull(x) else "No")

    hcu_sas = get_hcu(data_path)
    #
    # Merge data
    data = pd.merge(hcu_external_data, hcu_sas, left_on=['SUBJID', 'visit_trans', 'cat_trans'],
                    right_on=['Subject',
                              'FolderName',
                              'cat'],
                    how="outer")


    # # 反馈比较结果
    data = data.apply(compute_flags_and_vars_lab, axis=1)
    # Save data

    return data
