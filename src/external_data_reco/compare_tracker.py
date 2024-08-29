# -- coding: utf-8 --
__author__ = "ruijing.li"
__version__ = "0.1.0"

import logging
import datacompy
import pandas as pd
from datetime import datetime
from utils.common import sort_data


def compare_data_tracker_record(old_data: pd.DataFrame, new_data: pd.DataFrame, key_list: list,
                              not_compare_variables=None,
                         keep_delete_data=True) -> pd.DataFrame:
    old_data = old_data.drop(columns=["Issues Number"])
    old_data = old_data.fillna("").replace({"None": "", "Null": "", "nan": ""})

    if not_compare_variables is None:
        not_compare_variables = {}
    common_columns = old_data.columns.intersection(new_data.columns)

    compare_variables = common_columns.difference(not_compare_variables)

    not_compare_variables_new = key_list + [var for var in new_data.columns if var not in compare_variables]

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

    compare_add_or_delete = datacompy.Compare(OldDataSet, NewDataSet, join_columns=key_list)
    data_deleted = compare_add_or_delete.df1_unq_rows
    print(f"已解决的问题：{len(data_deleted)}")
    data_add = compare_add_or_delete.df2_unq_rows
    print(f"新增的问题：{len(data_add)}")

    data_compare_change = datacompy.Compare(OldDataSet, NewDataSet, join_columns=compare_variables)

    data_new = data_compare_change.df2_unq_rows
    data_old = data_compare_change.df1_unq_rows

    data_unchanged = data_compare_change.intersect_rows
    data_unchanged = data_unchanged.drop(["_merge"], axis=1)
    print(f"结果未变更的问题：{len(data_unchanged)}")

    data_new = pd.concat([data_new, data_add], ignore_index=True).drop_duplicates(keep=False)
    data_old = pd.concat([data_old, data_deleted], ignore_index=True).drop_duplicates(keep=False)

    key_list_lowercase = list(map(lambda x: x.lower(), key_list))
    data_concat = pd.merge(data_new, data_old, how="left", on=key_list_lowercase)
    print(f"结果变更的问题：{len(data_concat)}")
    data_change = pd.DataFrame()

    for (col_name, col_val) in data_concat.items():
        if len(data_concat) == 0:
            break

        elif col_name.endswith("_x"):
            prefix = col_name.replace("_x", "")
            New = prefix + "_x"
            Old = prefix + "_y"

            if prefix in {"data manager check personnel and date (dd-mmm-dd): comments",
                          "central lab responder and date (dd-mmm-dd): comments", "status",
                          "resolution date (dd-mmm-yyyy)"}:
                data_change[prefix] = data_concat.apply(
                    lambda x: str(x[Old]) if x[Old] != "" else str(x[New]),
                    axis=1)
            elif prefix in {"the record of database", "the record of central laboratory"}:
                data_change[prefix] = data_concat.apply(
                    lambda x: str(x[Old]) + " -> " + str(x[New]) if str(x[New]) != str(x[Old]) else str(x[New]),
                    axis=1)
            else:
                data_change[prefix] = data_concat.apply(lambda x: str(x[New]), axis=1)

        elif col_name.endswith("_y"):
            continue

        else:
            data_change[col_name] = data_concat[col_name]
            continue

    # 情况1：整行记录缺失
    # 行比较较为可能出现的情况：
    # 新增记录，输出本次comments，status应为open for site
    # 删除记录，即为已解决问题，status应为closed
    # 未变更记录，status输出上次信息

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
    print(data_all.columns)
    data_all = data_all[lowercase_columns]
    data_all = sort_data(data_all, key_list_lowercase)

    data_all["status_1"] = data_all.apply(
        lambda x: x["status"] if x["status"] != ""
        else "closed" if x["Flag"] == "Resolved" else "open for site", axis=1)

    data_all["resolution date (dd-mmm-yyyy)"] = data_all["resolution date (dd-mmm-yyyy)"].apply(
        lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S" ).strftime("%Y-%m-%d") if x != "" else "")

    data_all["resolution date (dd-mmm-yyyy)_1"] = data_all.apply(
        lambda x: x["resolution date (dd-mmm-yyyy)"] if x["resolution date (dd-mmm-yyyy)"] != ""
        else datetime.now().strftime("%Y-%m-%d") if x["status"] == "closed" else "", axis=1)

    data_all.drop(columns=["Flag", "status", "resolution date (dd-mmm-yyyy)"], inplace=True)
    data_all = data_all.rename(
        columns={"status_1": "status", "resolution date (dd-mmm-yyyy)_1": "resolution date (dd-mmm-yyyy)"})

    return data_all
