# -- coding: utf-8 --
__author__ = "ruijing.li"
__version__ = "0.1.0"

import pandas as pd
from data.reader import read_excel


def load_external_data(external_path):
    external_data = read_excel(external_path, "external_data")
    return external_data


def load_mapping_rules(external_path, dict_name, key_list, output_value):
    matching_rules_path = external_path + "/matching_rules.xlsx"
    df = pd.read_excel(matching_rules_path, sheet_name=dict_name, header=0)
    df = df.drop_duplicates(keep="first")
    # df_upper = df.applymap(lambda x: x.upper() if isinstance(x, str) and x else x)
    match_rules = df.set_index(key_list)[output_value].to_dict()
    return match_rules


def load_visit_mapping_rules(external_path):
    rules = load_mapping_rules(external_path, "folder", ["visit_name_external", "timepoint_external"], "visit_name_edc")
    return rules


def load_timepoint_mapping(external_path):
    rules = load_mapping_rules(external_path, "timepoint", ["timepoint_external"],"timepoint_edc")
    return rules


def load_category_mapping(external_path):
    rules = load_mapping_rules(external_path, "category", ["LBCAT"],"LBTEST_edc")#"LBTEST_external"
    return rules
