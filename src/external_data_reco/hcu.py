# -- coding: utf-8 --
__author__ = "ruijing.li"
__version__ = "0.1.0"

import logging
import pandas as pd
from data.sas_data import get_hcu
from data.external_data import load_visit_mapping_rules_hcu
from data.external_data import load_category_mapping
from utils.common import compute_flags_and_vars_lab


def external_data_reco_hcu(data_path, external_data, external_path) -> pd.DataFrame:
    """
    This function is used to reconciliation of external data for the given data.
    """
    logging.info("Start external data reconciliation...")
    logging.info("Data path: {}".format(data_path))

    external1 = external_data
    folder_mapping = load_visit_mapping_rules_hcu(external_path)
    logging.info("folder mapping for hcu is: {}".format(folder_mapping))
    category_mapping = load_category_mapping(external_path)
    logging.info("category mapping for hcu is: {}".format(category_mapping))

    # 处理外部数据,根据foldermapping，统一folder名称
    external = external1.loc[
        (external1.LBCAT == "Chemistry") | (external1.LBCAT == "Hematology") | (external1.LBCAT == "Urinalysis")][
        ["SUBJID", "LBREFID", "VISIT", 'LBTPT', "LBTEST", "LBCAT", "LBSTAT", "LBREASND", "LBDTC"]].drop_duplicates(
        keep='first')

    external["LBDTC_Date"] = external["LBDTC"].apply(lambda x: x.split("T")[0].strip() if x is not None else None)

    external["LBDTC_Time"] = external["LBDTC"].apply(
        lambda x: x.split("T")[1].strip() if x is not None else None)

    external['visit_trans'] = external[['VISIT']].apply(lambda x: folder_mapping.get(x.iloc[0], ''), axis=1)
    external['cat_trans'] = external[['LBCAT']].apply(lambda x: category_mapping.get(x.iloc[0], ''), axis=1)
    external['yn_trans'] = external['LBSTAT'].apply(lambda x: "Yes" if x=='' else "No")

    hcu_sas = get_hcu(data_path)
    #
    # Merge data
    data = pd.merge(external, hcu_sas, left_on=['SUBJID', 'visit_trans', 'LBCAT'],
                    right_on=['Subject',
                              'FolderName',
                              'cat'],
                    how="outer")
    # 去除nan，None，Null
    data = data.replace("None", "")
    data = data.replace("Null", "")
    data = data.replace("nan", "")
    # # 反馈比较结果
    data = data.apply(compute_flags_and_vars_lab, axis=1)
    data = data.sort_values(by=["Subject", "FolderSeq"])
    # Save data

    return data
