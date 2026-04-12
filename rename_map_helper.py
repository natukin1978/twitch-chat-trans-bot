from typing import Any, Dict

from csv_helper import read_csv_to_list


def read_rename_map() -> Dict[str, Any]:
    items = read_csv_to_list("rename_map.csv")
    result = {}
    for item in items:
        result[item[0]] = item[1:]
    return result
