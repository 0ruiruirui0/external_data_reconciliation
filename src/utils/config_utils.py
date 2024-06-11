# -- coding: utf-8 --
__author__ = "ruijing.li"
__version__ = "0.1.0"

SORT_COLUMNS_LAB = ["Subject", "FolderSeq"]

SORT_COLUMNS_DM = ["Subject"]

SYSTEM_COLUMNS = ["Subject", "InstanceName", "FolderName", "FolderSeq"]

ISSUE_TYPE = ["Missing in EDC but available in transfer.", "Missing in transfer but available in EDC.", "Inconsistent"]

ACTION_NEEDED = ["Site enter data in EDC.",
                 "Need site confirm whether transfer to vendor, if yes, provide requisition number, then DM will "
                 "confirm with vendor.",
                 "site resolve query."]

#
