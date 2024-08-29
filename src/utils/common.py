# -- coding: utf-8 --
__author__ = "ruijing.li"
__version__ = "0.1.0"

import pandas as pd
import datacompy


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
    row['External'] = '; '.join(str(item) for item in row['External']) if isinstance(row['External'], list) else row[
        'External']
    return row


def compute_flags_and_vars_lab(row):
    def append_issue(message_text, var, edc_data, external_data):
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
        row['Var'] = ""
        row['EDC'] = "Missing"
        row['External'] = ""

    elif not pd.isnull(row["Subject"]) and pd.isnull(row["SUBJID"]):
        row["Issue_type"] = "Missing in transfer but available in EDC."
        row["Message"] = "Missing in transfer but available in EDC."
        row['Var'] = ""
        row['EDC'] = ""
        row['External'] = "Missing"

    elif yn_same and dat_same and tim_same:
        row['Issue_type'] = ""
        row['Message'] = ""
        row['Var'] = ""
        row['EDC'] = ""
        row['External'] = ""

    else:
        if not yn_same:
            row['Issue_type'] = "Inconsistent"
            append_issue(
                f'The LBSTAT is ‘{row["LBSTAT"]}’ in transfer, but ‘{row["var1"]}’ is ‘{row["YN"]}’ in EDC. Please verify.',
                row["var1"], row["YN"], row["LBSTAT"])

        if not dat_same:
            row['Issue_type'] = "Inconsistent"
            append_issue(
                f'The LBDTC is ‘{row["LBDTC_Date"]}’ in transfer, but ‘{row["var2"]}’ is ‘{row["DAT_formatted"]}’ in '
                f'EDC. Please verify.',
                row["var2"], row["LBDTC_Date"], row["DAT_formatted"])
        if not tim_same:
            row['Issue_type'] = "Inconsistent"
            append_issue(
                f'The LBDTC is ‘{row["LBDTC_Time"]}’ in transfer, but ‘{row["var3"]}’ is ‘{row["TIM_formatted"]}’ in EDC. Please verify.',
                row["var3"], row["LBDTC_Time"], row["TIM_formatted"])

        row['Message'] = '; '.join([str(item).replace("None", "").replace("nan", "").replace("NaT", "") for item in
                                    message])
        row['Var'] = '; '.join([str(item).replace("None", "").replace("nan", "").replace("NaT", "") for item in vars])
        row['EDC'] = '; '.join([str(item).replace("None", "").replace("nan", "").replace("NaT", "") for item in edc])
        row['External'] = '; '.join(
            [str(item).replace("None", "").replace("nan", "").replace("NaT", "") for item in external])

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
                row["var1"], row["YN"], row["LBSTAT"])
        if not dat_same:
            row['Issue_type'] = "Inconsistent"
            append_issue(
                f'The LBDTC is ‘{row["LBDTC_Date"]}’ in transfer, but ‘{row["var2"]}’ is ‘{row["DAT_formatted"]}’ in '
                f'EDC. Please verify.',
                row["var2"], row["LBDTC_Date"], row["DAT_formatted"])
        if not sample_same:
            row['Issue_type'] = "Inconsistent"
            append_issue(
                f'The LBSPEC is ‘{row["LBSPEC"]}’ in transfer, but ‘{row["var3"]}’ is ‘{row["TERM"]}’ in EDC. '
                f'Please verify.',
                row["var3"], row["TERM"], row["LBSPEC"])
        if not result_same:
            row['Issue_type'] = "Inconsistent"
            append_issue(
                f'The LBSTRESC is ‘{row["LBSTRESC"]}’ in transfer, but ‘{row["var3"]}’ is ‘{row["RESULT"]}’ in EDC. Please verify.',
                row["var4"], row["RESULT"], row["LBSTRESC"])

        row['Message'] = '; '.join([str(item).replace("None", "").replace("nan", "").replace("NaT", "") for item in
                                    issues])
        row['Var'] = '; '.join([str(item).replace("None", "").replace("nan", "").replace("NaT", "") for item in vars])
        row['EDC'] = '; '.join([str(item).replace("None", "").replace("nan", "").replace("NaT", "") for item in edc])
        row['External'] = '; '.join(
            [str(item).replace("None", "").replace("nan", "").replace("NaT", "") for item in external])
    return row


def compute_flags_and_vars_ser(row):
    def append_issue(issue_type, var, edc_data, external_data):
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
                row["var1"], row["YN"], row["LBSTAT"])
        if not dat_same:
            row['Issue_type'] = "Inconsistent"
            append_issue(
                f'The LBDTC is ‘{row["LBDTC_Date"]}’ in transfer, but ‘{row["var2"]}’ is ‘{row["DAT_formatted"]}’ in EDC. Please verify.',
                row["var2"], row["DAT_formatted"], row["LBDTC_Date"])
        if not result_same:
            row['Issue_type'] = "Inconsistent"
            append_issue(
                f'The LBSTRESC is ‘{row["LBSTRESC"]}’ in transfer, but ‘{row["var3"]}’ is ‘{row["RESULT"]}’ in '
                f'EDC. Please verify.',
                row["var3"], row["RESULT"], row["LBSTRESC"])
        row['Message'] = '; '.join([str(item).replace("None", "").replace("nan", "").replace("NaT", "") for item in
                                    issues])
        row['Var'] = '; '.join([str(item).replace("None", "").replace("nan", "").replace("NaT", "") for item in vars])
        row['EDC'] = '; '.join([str(item).replace("None", "").replace("nan", "").replace("NaT", "") for item in edc])
        row['External'] = '; '.join(
            [str(item).replace("None", "").replace("nan", "").replace("NaT", "") for item in external])

    return row


def convert_dtype(data, column):
    return data[column].astype(int, errors='ignore').astype(str, errors='ignore')


def sort_data(data: pd.DataFrame, sort_key: list) -> pd.DataFrame:
    # data_clean = data.replace("nan", "").replace("None", "")
    # def try_convert_to_float(df, key):
    #     try:
    #         return float(df.loc[0, key])
    #     except ValueError:
    #         return df.loc[0, key]
    #
    # sort_key_1 = []
    # for i in sort_key:
    #     if type(try_convert_to_float(data, i)) == float:
    #         sort_key_1.append(i)
    #     else:
    #         continue
    # for column in sort_key_1:
    #     try:
    #         data[column] = data[column].astype(float)
    #     except ValueError:
    #         continue

    data_clean = data.sort_values(by=sort_key)
    # data_clean = Sorter(data_clean).data

    # for column in sort_key_1:
    #     data_clean[column] = convert_dtype(data_clean, column)
    return data_clean


def compare_data_common(old_data: pd.DataFrame, new_data: pd.DataFrame, key_list: list, not_compare_variables=None,
                        keep_delete_data=True, mark_color=True) -> pd.DataFrame:
    # 计算old_data和new_data的公共列
    if not_compare_variables is None:
        not_compare_variables = {}
    common_columns = old_data.columns.intersection(new_data.columns)

    # print("common_columns is：{0}".format(common_columns))

    # 从公共列中移除not_compare_variables中的变量
    compare_variables = common_columns.difference(not_compare_variables)
    # print("compare_variables is：{0}".format(common_columns))

    # not_compare_variables_old = key_list + [var for var in old_data.columns if var not in compare_variables]
    # # print("not_compare_variables_old is：{0}".format(not_compare_variables_old))

    not_compare_variables_new = key_list + [var for var in new_data.columns if var not in compare_variables]

    # print("not_compare_variables_new is：{0}".format(not_compare_variables_new))

    OldDataSet = old_data.fillna(' ')
    NewDataSet = new_data.fillna(' ')

    def get_not_compare_data(data: pd.DataFrame, variable: list) -> pd.DataFrame:
        variable = [var for var in variable if var in data.columns]
        ts = data[variable]
        ts = ts.rename(columns={var: var.lower() for var in variable})
        return ts

    not_compare_df_new = get_not_compare_data(NewDataSet, not_compare_variables_new)

    OldDataSet = OldDataSet.drop(columns=list(set(OldDataSet.columns).difference(set(compare_variables))))
    NewDataSet = NewDataSet.drop(columns=list(set(NewDataSet.columns).difference(set(compare_variables))))

    compare_AddOrDelete = datacompy.Compare(OldDataSet, NewDataSet, join_columns=key_list)

    data_deleted = compare_AddOrDelete.df1_unq_rows
    data_add = compare_AddOrDelete.df2_unq_rows

    data_compare_Change = datacompy.Compare(OldDataSet, NewDataSet, join_columns=compare_variables)

    data_new = data_compare_Change.df2_unq_rows
    data_old = data_compare_Change.df1_unq_rows

    data_unchanged = data_compare_Change.intersect_rows
    data_unchanged = data_unchanged.drop(["_merge"], axis=1)

    data_new = pd.concat([data_new, data_add], ignore_index=True).drop_duplicates(keep=False)
    data_old = pd.concat([data_old, data_deleted], ignore_index=True).drop_duplicates(keep=False)

    key_list_lowercase = list(map(lambda x: x.lower(), key_list))
    data_concat = pd.merge(data_new, data_old, how="left", on=key_list_lowercase)

    data_change = pd.DataFrame()

    for (col_name, col_val) in data_concat.items():
        if len(data_concat) == 0:
            break

        elif col_name.endswith("_x"):
            prefix = col_name.replace("_x", "")
            New = prefix + "_x"
            Old = prefix + "_y"
            if mark_color:
                data_change[prefix] = data_concat.apply(
                    lambda x: str(x[Old]) + " -> " + str(x[New]) if str(x[New]) != str(x[Old]) else str(x[New]),
                    axis=1)
            else:
                data_change[prefix] = data_concat.apply(
                    lambda x: str(x[New]) if str(x[New]) != str(x[Old]) else str(x[New]),
                    axis=1)

        elif col_name.endswith("_y"):
            continue

        else:
            data_change[col_name] = data_concat[col_name]
            continue

    data_deleted["Flag"] = "Resolved"
    data_add["Flag"] = "New"
    data_change["Flag"] = "Updated"
    data_unchanged["Flag"] = "Old"

    data_other = pd.concat([data_add, data_change, data_unchanged], ignore_index=True)

    if len(not_compare_df_new) > 0:
        data_other = data_other.merge(not_compare_df_new, how="left", on=key_list_lowercase)
    else:
        data_other = data_other

    if keep_delete_data:
        data_all = pd.concat([data_deleted, data_other], ignore_index=True)
    else:
        data_all = data_other

    data_all = data_all.fillna(' ').map(str)
    lowercase_columns = [col.lower() for col in new_data.columns.tolist()] + ["Flag"]
    data_all = data_all[lowercase_columns]
    data_all = sort_data(data_all, key_list_lowercase)
    return data_all



