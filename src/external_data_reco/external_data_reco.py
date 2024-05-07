# -*- coding: utf-8 -*-
__author__ = "ruijing.li"
__version__ = "0.1.0"

import pandas as pd
import numpy as np
import os
import sys
import openpyxl
import logging
from src.data.reader import read_sas_file
from src.data.writer import save_df_to_excel
from tests.config import *



# 获取当前文件的绝对路径
current_file_path = os.path.abspath(__file__)
# 获取当前文件的父目录
src_path = os.path.dirname(os.path.dirname(current_file_path))
project_path = os.path.abspath(os.path.join(src_path, os.pardir))
# 将项目路径设置为运行路径
os.chdir(project_path)

#TODO:
# 增加config文件读取
# from src.utils.config_utils import load_config
# config = load_config()
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def external_data_reco(data_path, output_path) -> pd.DataFrame:
    """
    This function is used to reconciliation of external data for the given data.
    """
    logging.info("Start external data reconciliation...")
    logging.info("Data path: {}".format(data_path))
    logging.info("Output path: {}".format(output_path))

    # Load data
    data = read_sas_file(data_path,"cm1")

    # reconciliation of external data
    external_data = pd.DataFrame(columns=data.columns)

    return external_data

    #
    # logging.info("External data recommendation completed.")



if __name__ == '__main__':
    # output_path = "data/external_data_reco.excel"
    # external_data_reco(data_path, output_path)


    test_data = '{0}\\test_data\\project1\\SAS\\'.format(project_path)
    output_path = '{0}\\test_data\\project1\\output'.format(project_path)


    if not os.path.exists(output_path):

        os.makedirs(output_path)

    data =external_data_reco(test_data, output_path)

    file = f"Output_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.xlsx"
    save_df_to_excel(data,output_path, file)


    print("********** Done! **********")


