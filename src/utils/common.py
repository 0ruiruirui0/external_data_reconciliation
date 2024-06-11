# -- coding: utf-8 --
__author__ = "ruijing.li"
__version__ = "0.1.0"

import pandas as pd


def compute_flags_and_vars_dm(row):
    age_conditions = (row['YOB_trans'] == row['AGE']) or (row["YOB_cal"] == row['AGE'])
    sex_condition = row['SEX_trans'] == row['SEX_x']
    row['EDC'] = ""
    row['External'] = ""

    if pd.isnull(row["Subject"]) and not pd.isnull(row["SUBJID"]):
        row["Issue_type"] = "Missing in EDC but available in transfer."
        row["Message"] = "Missing in EDC but available in transfer."
        row['Var'] = ""
        row['EDC'] = 'Missing'
        row['External'] = ""
    elif not pd.isnull(row["Subject"]) and pd.isnull(row["SUBJID"]):
        row["Issue_type"] = "Missing in transfer but available in EDC."
        row["Message"] = "Missing in transfer but available in EDC."
        row['Var'] = None
        row['EDC'] = ""
        row['External'] = 'Missing'
    elif age_conditions and sex_condition:
        row['Issue_type'] = None
        row['Message'] = None
        row['Var'] = None
        row['EDC'] = ""
        row['External'] = ""
    else:
        row['Issue_type'] = "Inconsistent"
        row['Message'] = []
        row['Var'] = []
        row['EDC'] = []
        row['External'] = []
        count = 1
        if not age_conditions:
            row['Message'].append('The YOB is ‘{0}’ in transfer, but AGE is ‘{1}’ in EDC. Please verify.'.format(
                row["YOB_trans"],
                row["AGE"]))
            row['Var'].append(f'{count}.AGE')
            row['EDC'].append(row["AGE"])
            row['External'].append(row["YOB"])

            count += 1
        if not sex_condition:
            row['Message'].append('The SEX is ‘{0}’ in transfer, but SEX is ‘{1}’ in EDC. Please verify.'.format(
                row["SEX_x"],
                row["SEX_y"]))
            row['Var'].append(f'{count}.SEX')
            row['EDC'].append(row["SEX_y"])
            row['External'].append(row["SEX_x"])
            count += 1

    row['Message'] = '; '.join(row['Message']) if isinstance(row['Message'], list) else row['Message']
    row['Var'] = '; '.join(row['Var']) if isinstance(row['Var'], list) else row['Var']
    row['EDC'] = '; '.join(row['EDC']) if isinstance(row['EDC'], list) else row['EDC']
    row['External'] = '; '.join(row['External']) if isinstance(row['External'], list) else row['External']
    return row


def compute_flags_and_vars_lab(row):
    def append_issue(message_text, var,edc_data,external_data):
        message.append(message_text)
        vars.append(f'{len(message)}.{var}')
        edc.append(edc_data)
        external.append(external_data)

    yn_same = row['yn_trans'] == row['YN']

    dat_same = True
    if (row['yn_trans'] == 'Yes' or row['YN'] == 'Yes') and (
        row['LBDTC_Date'] != row['DAT_formatted']): dat_same = False
    tim_same = True
    if 'TIM_formatted' in row and (row['yn_trans'] == 'Yes' or row['YN'] == 'Yes') and (
        row['LBDTC_Time'] != row['TIM_formatted']): tim_same = False

    message = []
    vars = []
    edc = []
    external = []

    if pd.isnull(row["Subject"]) and not pd.isnull(row["SUBJID"]):
        row["Issue_type"] = "Missing in EDC but available in transfer."
        row["Message"] = "Missing in EDC but available in transfer."
        row['Var'] = None
        row['EDC'] = "Missing"
        row['External'] = ""

    elif not pd.isnull(row["Subject"]) and pd.isnull(row["SUBJID"]):
        row["Issue_type"] = "Missing in transfer but available in EDC."
        row["Message"] = "Missing in transfer but available in EDC."
        row['Var'] = None
        row['EDC'] = ""
        row['External'] = "Missing"

    elif yn_same and dat_same and tim_same:
        row['Issue_type'] = None
        row['Message'] = None
        row['Var'] = None
        row['EDC'] = ""
        row['External'] = ""

    else:
        if not yn_same:
            row['Issue_type'] = "Inconsistent"
            append_issue(
                f'The LBSTAT is ‘{row["yn_trans"]}’ in transfer, but ‘{row["var1"]}’ is ‘{row["YN"]}’ in EDC. Please verify.',
                row["var1"],row["YN"],row["LBSTAT"])

        if not dat_same:
            row['Issue_type'] = "Inconsistent"
            append_issue(
                f'The LBDTC is ‘{row["LBDTC_Date"]}’ in transfer, but ‘{row["var2"]}’ is ‘{row["DAT_formatted"]}’ in '
                f'EDC. Please verify.',
                row["var2"],row["LBDTC_Date"],row["DAT_formatted"])
        if not tim_same:
            row['Issue_type'] = "Inconsistent"
            append_issue(
                f'The LBDTC is ‘{row["LBDTC_Time"]}’ in transfer, but ‘{row["var3"]}’ is ‘{row["TIM_formatted"]}’ in EDC. Please verify.',
                row["var3"],row["LBDTC_Time"],row["TIM_formatted"])

        row['Message'] = '; '.join([str(item) for item in message])
        row['Var'] = '; '.join([str(item) for item in vars])
        row['EDC'] = '; '.join([str(item) for item in edc])
        row['External'] = '; '.join([str(item) for item in external])

    return row


def compute_flags_and_vars_preg(row):
    def append_issue(issue_type, var, edc_data, external_data):
        issues.append(issue_type)
        vars.append(f'{len(issues)}.{var}')
        edc.append(edc_data)
        external.append(external_data)

    yn_same = row['yn_trans'] == row['YN']

    dat_same = True
    if (row['yn_trans'] == 'Yes' or row['YN'] == 'Yes') and (
        row['FolderName'] == 'Screening' or row['FolderName'] == 'Unscheduled Visit') and (
        row['LBDTC_Date'] != row['DAT_formatted']): dat_same = False

    sample_same = True
    if (row['yn_trans'] == 'Yes' or row['YN'] == 'Yes') and (
        str(row['LBSPEC']).upper() != str(row['TERM']).upper()): sample_same = False

    result_same = True
    if (row['yn_trans'] == 'Yes' or row['YN'] == 'Yes') and (
        str(row['LBSTRESC']).upper() != str(row['RESULT']).upper()): result_same = False

    issues = []
    vars = []
    edc = []
    external = []

    if pd.isnull(row["Subject"]) and not pd.isnull(row["SUBJID"]):
        row["Issue_type"] = "Missing in EDC but available in transfer."
        row["Message"] = "Missing in EDC but available in transfer."
        row['Var'] = None
        row['EDC'] = "Missing"
        row['External'] = ""

    elif not pd.isnull(row["Subject"]) and pd.isnull(row["SUBJID"]):
        row["Issue_type"] = "Missing in transfer but available in EDC."
        row["Message"] = "Missing in transfer but available in EDC."
        row['Var'] = None
        row['EDC'] = ""
        row['External'] = "Missing"

    elif yn_same and dat_same and sample_same and result_same:
        row['Issue_type'] = None
        row['Message'] = None
        row['Var'] = None
        row['EDC'] = ""
        row['External'] = ""

    else:
        if not yn_same:
            row['Issue_type'] = "Inconsistent"
            append_issue(
                f'The LBSTAT is ‘{row["yn_trans"]}’ in transfer, but ‘{row["var1"]}’ is ‘{row["YN"]}’ in EDC. Please '
                f'verify.',
                row["var1"],row["YN"],row["LBSTAT"])
        if not dat_same:
            row['Issue_type'] = "Inconsistent"
            append_issue(
                f'The LBDTC is ‘{row["LBDTC_Date"]}’ in transfer, but ‘{row["var2"]}’ is ‘{row["DAT_formatted"]}’ in '
                f'EDC. Please verify.',
                row["var2"],row["LBDTC_Date"],row["DAT_formatted"])
        if not sample_same:
            row['Issue_type'] = "Inconsistent"
            append_issue(
                f'The LBSPEC is ‘{row["LBSPEC"]}’ in transfer, but ‘{row["var3"]}’ is ‘{row["TERM"]}’ in EDC. '
                f'Please verify.',
                row["var3"],row["TERM"],row["LBSPEC"])
        if not result_same:
            row['Issue_type'] = "Inconsistent"
            append_issue(
                f'The LBSTRESC is ‘{row["LBSTRESC"]}’ in transfer, but ‘{row["var3"]}’ is ‘{row["RESULT"]}’ in EDC. Please verify.',
                row["var4"],row["RESULT"],row["LBSTRESC"])

        row['Message'] = '; '.join([str(item) for item in issues])
        row['Var'] = '; '.join([str(item) for item in vars])
        row['EDC'] = '; '.join([str(item) for item in edc])
        row['External'] = '; '.join([str(item) for item in external])

    return row


def compute_flags_and_vars_ser(row):
    def append_issue(issue_type, var,edc_data, external_data):
        issues.append(issue_type)
        vars.append(f'{len(issues)}.{var}')
        edc.append(edc_data)
        external.append(external_data)

    yn_same = row['yn_trans'] == row['YN']

    dat_same = True
    if (row['yn_trans'] == 'Yes' or row['YN'] == 'Yes') and (
        row['LBDTC_Date'] != row['DAT_formatted']): dat_same = False

    result_same = True
    if (row['yn_trans'] == 'Yes' or row['YN'] == 'Yes') and (
        str(row['res_trans']).upper() != str(row['RESULT']).upper()): result_same = False

    issues = []
    vars = []
    edc = []
    external = []

    if pd.isnull(row["Subject"]) and not pd.isnull(row["SUBJID"]):
        row["Issue_type"] = "Missing in EDC but available in transfer."
        row['Message'] = "Missing in EDC but available in transfer."
        row['Var'] = None
        row['EDC'] = "Missing"
        row['External'] = ""
    elif not pd.isnull(row["Subject"]) and pd.isnull(row["SUBJID"]):
        row["Issue_type"] = "Missing in transfer but available in EDC."
        row['Message'] = "Missing in transfer but available in EDC."
        row['Var'] = None
        row['EDC'] = ""
        row['External'] = "Missing"
    elif yn_same and dat_same and result_same:
        row['Issue_type'] = None
        row['Issue_type'] = None
        row['Var'] = None
        row['EDC'] = ""
        row['External'] = ""
    else:
        if not yn_same:
            row['Issue_type'] = "Inconsistent"
            append_issue(
                f'The LBSTAT is ‘{row["yn_trans"]}’ in transfer, but ‘{row["var1"]}’ is ‘{row["YN"]}’ in EDC. '
                f'Please verify.',
                row["var1"],row["YN"],row["LBSTAT"])
        if not dat_same:
            row['Issue_type'] = "Inconsistent"
            append_issue(
                f'The LBDTC is ‘{row["LBDTC_Date"]}’ in transfer, but ‘{row["var2"]}’ is ‘{row["DAT_formatted"]}’ in EDC. Please verify.',
                row["var2"],row["DAT_formatted"],row["LBDTC_Date"])
        if not result_same:
            row['Issue_type'] = "Inconsistent"
            append_issue(
                f'The LBSTRESC is ‘{row["LBSTRESC"]}’ in transfer, but ‘{row["var3"]}’ is ‘{row["RESULT"]}’ in '
                f'EDC. Please verify.',
                row["var3"],row["RESULT"],row["LBSTRESC"])

        row['Message'] = '; '.join([str(item) for item in issues])
        row['Var'] = '; '.join([str(item) for item in vars])
        row['EDC'] = '; '.join([str(item) for item in edc])
        row['External'] = '; '.join([str(item) for item in external])

    return row

