# -- coding: utf-8 --
__author__ = "ruijing.li"
__version__ = "0.1.0"

import pandas as pd


def compute_flags_and_vars_dm(row):
    age_conditions = (row['YOB_trans'] == row['AGE']) or (row["YOB_cal"] == row['AGE'])
    sex_condition = row['SEX_trans'] == row['SEX_x']

    if pd.isnull(row["Subject"]) and not pd.isnull(row["SUBJID"]):
        row["Issue_type"] = "Missing in EDC but available in transfer."
        row['Var'] = None
    elif not pd.isnull(row["Subject"]) and pd.isnull(row["SUBJID"]):
        row["Issue_type"] = "Missing in transfer but available in EDC."
        row['Var'] = None
    elif age_conditions and sex_condition:
        row['Issue_type'] = None
        row['Var'] = None
    else:
        row['Issue_type'] = []
        row['Var'] = []
        count = 1
        if not age_conditions:
            row['Issue_type'].append('The YOB is ‘{0}’ in transfer, but AGE is ‘{1}’ in EDC. Please verify.'.format(
                row["YOB_trans"],
                row["AGE"]))
            row['Var'].append(f'{count}.AGE')
            count += 1
        if not sex_condition:
            row['Issue_type'].append('The SEX is ‘{0}’ in transfer, but SEX is ‘{1}’ in EDC. Please verify.'.format(
                row["SEX_x"],
                row["SEX_y"]))
            row['Var'].append(f'{count}.SEX')
            count += 1

    row['Issue_type'] = '; '.join(row['Issue_type']) if isinstance(row['Issue_type'], list) else row['Issue_type']
    row['Var'] = '; '.join(row['Var']) if isinstance(row['Var'], list) else row['Var']
    return row


def compute_flags_and_vars_lab(row):
    yn_conditions = row['yn_trans'] == row['YN']
    # dat_condition = (row['yn_trans'] == 'Yes' or row['YN'] == row['Yes']) and (row['LBDTC_Date'] == row[
    # 'DAT_formatted'])
    dat_condition = 'true'
    if (row['yn_trans'] == 'Yes' or row['YN'] == 'Yes') and (row['LBDTC_Date'] != row['DAT_formatted']):
        dat_condition = 'false'

    if pd.isnull(row["Subject"]) and not pd.isnull(row["SUBJID"]):
        row["Issue_type"] = "Missing in EDC but available in transfer."
        row['Var'] = None
    elif not pd.isnull(row["Subject"]) and pd.isnull(row["SUBJID"]):
        row["Issue_type"] = "Missing in transfer but available in EDC."
        row['Var'] = None
    elif yn_conditions and dat_condition:
        row['Issue_type'] = None
        row['Var'] = None
    else:
        row['Issue_type'] = []
        row['Var'] = []
        count = 1
        if not yn_conditions:
            row['Issue_type'].append('The ‘{0}’ is ‘{1}’ in transfer, but ‘{0}’ is ‘{2}’ in EDC. Please verify.'.format(
                row["cat"],
                row["yn_trans"],
                row["YN"]))
            row['Var'].append(f'{count}.{row["cat"]}')
            count += 1
        if not dat_condition:
            row['Issue_type'].append('The ‘{0}’ is ‘{1}’ in transfer, but ‘{0}’ is ‘{2}’ in EDC. Please verify.'.format(
                row["cat2"],
                row["LBDTC_Date"],
                row["DAT_formatted"]))
            row['Var'].append(f'{count}.{row["cat2"]}')
            count += 1

    row['Issue_type'] = '; '.join(row['Issue_type']) if isinstance(row['Issue_type'], list) else row['Issue_type']
    row['Var'] = '; '.join(row['Var']) if isinstance(row['Var'], list) else row['Var']
    return row
